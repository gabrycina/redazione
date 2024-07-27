from app.db import Base
from sqlalchemy import Column, Integer, String


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    drafter_prompt = Column(String, nullable=True)
    sources = Column(String, nullable=True)
    history = Column(String, default="[]")
    subscription_code = Column(String, nullable=True, unique=True)
