from typing import List, Optional

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
            image: Optional[UploadFile] = Form(None, description="image description"),
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
    image: Optional[str]
    created_at: int
    updated_at: int


class DestinationPaginationModel(BaseModel):
    page_number: int
    page_size: int
    total: int
    total_pages: int
    destinations: List[DestinationModel]
