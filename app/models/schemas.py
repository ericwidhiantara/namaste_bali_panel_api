from pydantic import BaseModel, Field


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class UserAuth(BaseModel):
    email: str = Field(..., description="user email")
    password: str = Field(..., min_length=5, max_length=24, description="user password")


class UserOut(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    username: str
    is_active: bool


class SystemUser(UserOut):
    password: str


class MessageModel(BaseModel):
    sender_id: str
    recipient_id: str
    message: str
    is_read: bool = False
