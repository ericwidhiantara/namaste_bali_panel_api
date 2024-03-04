from fastapi import Form
from pydantic import BaseModel, EmailStr


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class UserAuth(BaseModel):
    first_name: str = Form(..., description="user first name")
    last_name: str = Form(..., description="user last name")
    username: str = Form(..., description="user username")
    email: EmailStr = Form(..., description="user email")
    password: str = Form(..., min_length=6, max_length=24, description="user password")


class UserModel(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    username: str
    is_active: bool


class SystemUser(UserModel):
    password: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None
    user: UserModel = None


class MessageModel(BaseModel):
    sender_id: str
    recipient_id: str
    message: str
    is_read: bool = False
