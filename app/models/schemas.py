from typing import TypeVar, Generic, List

from fastapi import Form, UploadFile
from pydantic import BaseModel, EmailStr

from app.utils.helper import form_body

M = TypeVar("M", bound=BaseModel)


class Meta(BaseModel):
    code: int = 200
    message: str = "OK"
    error: bool = False


class BaseResp(BaseModel, Generic[M]):
    meta: Meta = Meta()
    data: M = None  # support any object


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


@form_body
class FormUserModel(BaseModel):
    first_name: str = Form(..., description="user first name")
    last_name: str = Form(..., description="user last name")
    username: str = Form(..., description="user username")
    email: EmailStr = Form(..., description="user email")
    password: str = Form(..., min_length=6, max_length=24, description="user password")
    phone: str = Form(..., description="user phone number")
    picture: UploadFile = Form(..., description="user picture")


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


@form_body
class FormPortfolioModel(BaseModel):
    title: str = Form(..., description="portfolio title")
    description: str = Form(..., description="portfolio description")
    images: List[UploadFile] = Form(..., description="portfolio picture")
    date_started: str = Form(..., description="portfolio date started")
    date_finished: str = Form(..., description="portfolio date finished")


@form_body
class FormEditPortfolioModel(BaseModel):
    id: str = Form(..., description="portfolio id")
    title: str = Form(..., description="portfolio title")
    description: str = Form(..., description="portfolio description")
    images: List[UploadFile] = Form(..., description="portfolio picture")
    date_started: str = Form(..., description="portfolio date started")
    date_finished: str = Form(..., description="portfolio date finished")


@form_body
class FormDeletePortfolioModel(BaseModel):
    id: str = Form(..., description="portfolio id")


class PortfolioModel(BaseModel):
    id: str
    title: str
    description: str
    images: List[str]
    date_started: str
    date_finished: str
    created_at: int
    updated_at: int
