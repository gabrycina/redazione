import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from app.db import get_db, Base, engine
from app.models import User
from app.schemas import BasicResponse, UserPost, UserResponse, UserUpdate
from app.core import get_basic_pipeline, Crawler2
from app.notify import EmailNotifier


logger = logging.getLogger(__name__)

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

pipeline = get_basic_pipeline(API_KEY)
email_notifier = EmailNotifier(RESEND_API_KEY)
Base.metadata.create_all(bind=engine)
app = FastAPI()

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


def redact(user):
    if not user.sources or not user.drafter_prompt:
        logging.warning(f"Attempted to send email to user not intialized {user.email}")
        return

    sources = user.sources.split("|")
    try:
        report = pipeline.run(
            input=sources,
            context={
                "drafter": user.drafter_prompt + ": {}",
                "summarizer": "Here's the article: {}",
                "reporter": "Here's today's articles selection, write the newsletter: {}",
            },
        )
    except Exception as e:
        logging.error(f"Pipeline: error not caught {e}")
        return

    email_notifier.notify(body=report, to_email=user.email)


@app.get("/send_email/{user_id}")
async def send_email(
    user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
) -> BasicResponse:
    try:
        user = db.query(User).filter(User.id == user_id).one()
    except Exception as e:
        logging.error(f"send_email: {e}")
        raise HTTPException(status_code=404, detail="User not found")
    background_tasks.add_task(redact, user)
    return BasicResponse(msg="sending email in background...")


@app.post("/users/")
async def register(user: UserPost, db: Session = Depends(get_db)) -> BasicResponse:
    try: 
        user_db = User(**user.model_dump())
        db.add(user_db)
        db.commit()
        db.refresh(user_db)
    except Exception as e:
        logging.error(f"Register: {e}")
        raise HTTPException(status_code=404, detail="an error occurred")
    return BasicResponse(msg="ok")


@app.get("/users/")
async def get_all_users(db: Session = Depends(get_db)) -> list[UserResponse]:
    try:
        users = db.query(User).all()
    except Exception as e:
        logging.error(f"get_all_users: {e}")
        raise HTTPException(status_code=404, detail="an error occurred")
    return list(users)


@app.put("/users/{user_id}")
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
        logging.error(f"get_all_users: {e}")
        raise HTTPException(status_code=404, detail="an error occurred")
    return BasicResponse(msg="ok")


@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)) -> BasicResponse:
    try:
        user_db = db.query(User).filter(User.id == user_id).one()
        db.delete(user_db)
        db.commit()
    except Exception as e:
        logging.error(f"delete_user: {e}")
        raise HTTPException(status_code=404, detail="an error occurred")
    return BasicResponse(msg="ok")
