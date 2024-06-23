import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from app.db import get_db, Base, engine
from app.models import User
from app.schemas import BasicResponse, UserPost, UserResponse, UserUpdate
from app.core import get_basic_pipeline
from app.notify import EmailNotifier

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
SMTP_USER = os.getenv("EMAIL_USER")
SMTP_PASSWORD = os.getenv("EMAIL_PASSWORD")

pipeline = get_basic_pipeline(API_KEY)
email_notifier = EmailNotifier(SMTP_USER, SMTP_PASSWORD)
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
    sources = user.sources.split("|")
    report = pipeline.run(
        input=sources,
        context={
            "drafter": user.drafter_prompt + ": {}",
            "summarizer": "Here's the article: {}",
            "reporter": "Here's today's articles selection, write the newsletter: {}",
        },
    )
    email_notifier.notify(body=report, to_email=user.email)


@app.get("/send_email/{user_id}")
async def send_email(
    user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
) -> BasicResponse:
    user = db.query(User).filter(User.id == user_id).one()
    background_tasks.add_task(redact, user)
    return BasicResponse(msg="ok")


@app.post("/users/")
async def register(user: UserPost, db: Session = Depends(get_db)) -> BasicResponse:
    user_db = User(**user.model_dump())
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    print(user_db)
    return BasicResponse(msg="ok")


@app.get("/users/")
async def get_all_users(db: Session = Depends(get_db)) -> list[UserResponse]:
    users = db.query(User).all()
    return list(users)


@app.put("/users/{user_id}/")
async def update_user(
    user_id: int, user: UserUpdate, db: Session = Depends(get_db)
) -> BasicResponse:
    user_db = db.query(User).filter(User.id == user_id).one()
    for var, value in vars(user).items():
        if value:
            setattr(user_db, var, value)
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return BasicResponse(msg="ok")


@app.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)) -> BasicResponse:
    user_db = db.query(User).filter(User.id == user_id).one()
    db.delete(user_db)
    db.commit()
    return BasicResponse(msg="ok")
