from fastapi import Form, UploadFile
from pydantic import BaseModel, EmailStr


class FormUserModel:

    def __init__(
            self,
            first_name: str = Form(..., description="user first name"),
            last_name: str = Form(..., description="user last name"),
            username: str = Form(..., description="user username"),
            email: EmailStr = Form(..., description="user email"),
            password: str = Form(..., min_length=6, max_length=24, description="user password"),
            phone: str = Form(..., description="user phone number"),
            picture: UploadFile = Form(..., description="user picture"),
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.email = email
        self.password = password
        self.phone = phone
        self.picture = picture


class UserModel(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    username: str
    phone: str
    picture: str
    is_active: bool
    created_at: int
    updated_at: int


class SystemUser(UserModel):
    password: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None
    user: UserModel = None
