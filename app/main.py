from fastapi import FastAPI, Depends
from pydantic import BaseModel
from app.db import get_db, User
from sqlalchemy.orm import Session
from app.core import redact

app = FastAPI()

class BasicResponse(BaseModel):
    msg: str


class UserPost(BaseModel):
    email: str

class UserResponse(BaseModel):
    id: int
    email: str

@app.post("/send_email/")
async def send_email(email: str) -> BasicResponse:
    redact(email)
    return BasicResponse(msg="sending it...")


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