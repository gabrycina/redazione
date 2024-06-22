import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.db import get_db, Base, engine
from app.models import User
from app.schemas import BasicResponse, UserPost, UserResponse
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


@app.post("/send_email/")
async def send_email(email: str) -> BasicResponse:
    # prendere user dal db
    # mettere il suo prompt nel contesto
    report = pipeline.run(
        input=["https://news.ycombinator.com/from?site=arxiv.org"],
        context={
            "drafter": "Here's today papers, write the newsletter: {}",
            "reporter": "Here's today papers, write the newsletter: {}",
        },
    )
    email_notifier.notify(body=report, to_email=email)
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
