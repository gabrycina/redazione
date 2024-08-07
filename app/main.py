import os
import logging
import json
import random
import string
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from sqlalchemy import text, or_
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from datetime import date

from app.db import get_db, Base, engine
from app.models import User
from app.schemas import BasicResponse, UserPost, UserResponse, UserUpdate
from app.core import get_basic_pipeline
from app.notify import EmailNotifier

from app.constants.emails import WELCOME_EMAIL

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

pipeline = get_basic_pipeline(API_KEY)
email_notifier = EmailNotifier(RESEND_API_KEY)

Base.metadata.create_all(bind=engine)
app = FastAPI()
scheduler = AsyncIOScheduler(
    jobstores={"default": MemoryJobStore()}, timezone="Europe/London"
)
scheduler.start()

origins = [
    "http://localhost:5173",  # React app origin
    "http://redact.lofipapers.com",
    "https://redact.lofipapers.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@scheduler.scheduled_job("cron", day_of_week="mon-sun", hour=10, minute=54, second=0)
def cron_job():
    logger.info("Starting cron job")
    db = next(get_db())
    users = db.query(User).all()
    for user in users:
        redact(user)
    logger.info("Ending cron job")


def redact(user):
    if not user.sources or not user.drafter_prompt:
        logger.warning(f"Attempted to send email to user not intialized {user.email}")
        return

    sources = user.sources.split("|")
    try:
        report = pipeline.run(
            input=sources,
            context={
                "drafter": user.drafter_prompt + ": {}",
                "summarizer": "Here's the article: {}",
                "reporter": "Here's today's articles selection, write the newsletter: {}",
                "history": json.loads(user.history),
                "user_id": user.id,
            },
        )
    except Exception as e:
        logger.error(f"pipeline: {e}")
        return

    email_notifier.notify(
        subject=f"Daily Redact 📬 - {date.today().strftime('%d-%m-%Y')}",
        body=report,
        to_email=user.email,
    )


@app.get("/send_email/{user_id}", tags=["notication"])
async def send_email(
    user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
) -> BasicResponse:
    try:
        user = db.query(User).filter(User.id == user_id).one()
    except Exception as e:
        logger.error(f"send_email: {e}")
        raise HTTPException(status_code=404, detail="User not found")
    background_tasks.add_task(redact, user)
    return BasicResponse(detail="sending email in background...")


@app.post("/users/", tags=["user"])
async def register(user: UserPost, db: Session = Depends(get_db)) -> BasicResponse:
    try:
        user_db = User(**user.model_dump())
        user_db.subscription_code = generate_random_string(8)
        db.add(user_db)
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        logger.error(f"Register: {e}")
        raise HTTPException(status_code=404, detail="an error occurred")

    email = WELCOME_EMAIL.format(subscription_code=user_db.subscription_code)

    email_notifier.notify(
        email,
        user.email,
        subject="😬 One last step: choose your sources and preferences!",
    )
    return BasicResponse(detail="ok")


@app.get("/users/", tags=["user"])
async def get_all_users(db: Session = Depends(get_db)) -> list[UserResponse]:
    try:
        users = db.query(User).all()
    except Exception as e:
        logger.error(f"get_all_users: {e}")
        raise HTTPException(status_code=404, detail="an error occurred")
    return list(users)


@app.post("/users/{subscription_code}", tags=["user"])
async def complete_user_subscription(
    subscription_code: str, user: UserUpdate, db: Session = Depends(get_db)
) -> BasicResponse:
    try:
        user_db = (
            db.query(User).filter(User.subscription_code == subscription_code).one()
        )
        for var, value in vars(user).items():
            if value:
                setattr(user_db, var, value)
        user_db.subscription_code = None
        db.add(user_db)
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        logger.error(f"complete_user_subscription: {e}")
        raise HTTPException(status_code=404, detail="an error occurred")
    return BasicResponse(detail="ok")


@app.put("/users/{user_id}", tags=["user"])
async def update_user(
    user_id: int, user: UserUpdate, db: Session = Depends(get_db)
) -> BasicResponse:
    try:
        user_db = db.query(User).filter(User.id == user_id).one()
        for var, value in vars(user).items():
            if value:
                setattr(user_db, var, value)
        db.add(user_db)
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        logger.error(f"update_user: {e}")
        raise HTTPException(status_code=404, detail="an error occurred")
    return BasicResponse(detail="ok")


@app.delete("/users/{user_id}", tags=["user"])
async def delete_user(user_id: int, db: Session = Depends(get_db)) -> BasicResponse:
    try:
        user_db = db.query(User).filter(User.id == user_id).one()
        db.delete(user_db)
        db.commit()
    except Exception as e:
        logger.error(f"delete_user: {e}")
        raise HTTPException(status_code=404, detail="an error occurred")
    return BasicResponse(detail="ok")


@app.get("/migrations", tags=["database"])
async def apply_migrations() -> BasicResponse:
    try:
        connection = engine.connect()
        connection.execute(text("ALTER TABLE users ADD COLUMN subscription_code TEXT;"))
        connection.execute(
            text(
                "CREATE UNIQUE INDEX idx_users_department ON users(subscription_code);"
            )
        )
    except Exception as e:
        logger.error(f"Migrations Error: {e}")
        raise HTTPException(status_code=404, detail=e)
    finally:
        connection.close()
    temp_update_user()
    return BasicResponse(detail="ok")


def temp_update_user():
    logger.info("Starting updating non register user")
    db = next(get_db())
    users = (
        db.query(User)
        .filter(or_(User.drafter_prompt == None, User.sources == None))
        .all()
    )
    for user in users:
        try:
            user.subscription_code = generate_random_string(8)
            db.add(user)
            db.commit()
            db.refresh(user)
        except Exception as e:
            logger.error("Error occurred while updating user: {e}")


def generate_random_string(length):
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choice(characters) for _ in range(length))
    return random_string
