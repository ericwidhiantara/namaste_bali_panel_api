from fastapi import Form, UploadFile
from pydantic import BaseModel


class FormDestinationModel:

    def __init__(
            self,
            title: str = Form(..., description="destination title"),
            description: str = Form(..., description="destination description"),
            image: UploadFile = Form(..., description="image description"),
    ):
        self.title = title
        self.description = description
        self.image = image


class FormEditDestinationModel:
    def __init__(
            self,
            id: str = Form(..., description="destination id"),
            title: str = Form(..., description="destination title"),
            description: str = Form(..., description="destination description"),
            image: UploadFile = Form(..., description="image description"),
    ):
        self.id = id
        self.title = title
        self.description = description
        self.image = image


class DestinationModel(BaseModel):
    id: str
    title: str
    slug: str
    description: str
    image: str
    created_at: int
    updated_at: int
