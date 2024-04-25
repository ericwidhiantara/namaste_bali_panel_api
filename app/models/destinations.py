from fastapi import Form, UploadFile
from pydantic import BaseModel

from app.utils.helper import form_body


@form_body
class FormDestinationModel(BaseModel):
    title: str = Form(..., description="destination title")
    description: str = Form(..., description="destination description")
    image: UploadFile = Form(..., description="image description")


@form_body
class FormEditDestinationModel(BaseModel):
    id: str = Form(..., description="destination id")
    title: str = Form(..., description="destination title")
    description: str = Form(..., description="destination description")
    image: UploadFile = Form(..., description="image description")


class DestinationModel(BaseModel):
    id: str
    title: str
    slug: str
    description: str
    image: str
    created_at: int
    updated_at: int
