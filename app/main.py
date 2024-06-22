import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session

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

def redact(user):
    sources = user.sources.split("|")
    report = pipeline.run(
        input=sources,
        context={
            "drafter": user.drafter_prompt + ": {}",
            "reporter": "Here's today papers, write the newsletter: {}",
        },
    )
    email_notifier.notify(body=report, to_email=user.email)

@app.get("/send_email/{id}")
async def send_email(id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> BasicResponse:
    user = db.query(User).filter(User.id == id).one()
    background_tasks.add_task(redact, user)
    return BasicResponse(msg="ok")


@app.post("/register/")
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
async def update_user(user_id:int, user: UserUpdate,db: Session = Depends(get_db)) -> BasicResponse:
    user_db = db.query(User).filter(User.id == user_id).one()
    for var, value in vars(user).items():
        if value:
            setattr(user_db, var, value) 
    db.add(user_db)
    db.commit()
    db.refresh(user_db)
    return BasicResponse(msg="ok")