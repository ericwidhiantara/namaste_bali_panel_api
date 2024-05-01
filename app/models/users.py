from typing import List

from fastapi import Form, UploadFile
from pydantic import BaseModel, EmailStr


class FormUserModel:

    def __init__(
            self,
            name: str = Form(..., description="user name"),
            username: str = Form(..., description="user username"),
            email: EmailStr = Form(..., description="user email"),
            password: str = Form(..., min_length=6, max_length=24, description="user password"),
            phone: str = Form(..., description="user phone number"),
            picture: UploadFile = Form(..., description="user picture"),
    ):
        self.name = name
        self.username = username
        self.email = email
        self.password = password
        self.phone = phone
        self.picture = picture


class FormEditUserModel:

    def __init__(
            self,
            id: str = Form(..., description="user id"),
            name: str = Form(..., description="user name"),
            username: str = Form(..., description="user username"),
            email: EmailStr = Form(..., description="user email"),
            password: str = Form(..., min_length=6, max_length=24, description="user password"),
            phone: str = Form(..., description="user phone number"),
            picture: UploadFile = Form(..., description="user picture"),
    ):
        self.id = id
        self.name = name
        self.username = username
        self.email = email
        self.password = password
        self.phone = phone
        self.picture = picture


class UserModel(BaseModel):
    id: str
    email: str
    name: str
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


class UserPaginationModel(BaseModel):
    page_number: int
    page_size: int
    total: int
    total_pages: int
    users: List[UserModel]
