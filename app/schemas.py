from pydantic import BaseModel


class BasicResponse(BaseModel):
    msg: str


class UserPost(BaseModel):
    email: str


class UserResponse(BaseModel):
    id: int
    email: str
