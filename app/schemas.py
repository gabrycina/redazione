from pydantic import BaseModel


class BasicResponse(BaseModel):
    detail: str


class UserPost(BaseModel):
    email: str


class UserResponse(BaseModel):
    id: int
    email: str
    drafter_prompt: str | None
    sources: str | None
    history: str | None


class UserUpdate(BaseModel):
    drafter_prompt: str | None = None
    sources: str | None = None
    history: str | None = None
