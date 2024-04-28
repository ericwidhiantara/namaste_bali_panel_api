from typing import Optional, List

from fastapi import Form, UploadFile
from pydantic import BaseModel


class FormTeamModel:

    def __init__(
            self,
            name: str = Form(..., description="team name"),
            email: str = Form(..., description="team email"),
            whatsapp: str = Form(..., description="team whatsapp"),
            facebook: Optional[str] = Form(None, description="team facebook"),  # Make optional
            instagram: Optional[str] = Form(None, description="team instagram"),  # Make optional
            twitter: Optional[str] = Form(None, description="team twitter"),  # Make optional
            tiktok: Optional[str] = Form(None, description="team tiktok"),  # Make optional
            role: str = Form(..., description="team role"),
            address: str = Form(..., description="team address"),
            image: UploadFile = Form(..., description="image description"),
    ):
        self.name = name
        self.email = email
        self.whatsapp = whatsapp
        self.facebook = facebook
        self.instagram = instagram
        self.twitter = twitter
        self.tiktok = tiktok
        self.role = role
        self.address = address
        self.image = image


class FormEditTeamModel:

    def __init__(
            self,
            id: str = Form(..., description="team id"),
            name: str = Form(..., description="team name"),
            email: str = Form(..., description="team email"),
            whatsapp: str = Form(..., description="team whatsapp"),
            facebook: Optional[str] = Form(None, description="team facebook"),  # Make optional
            instagram: Optional[str] = Form(None, description="team instagram"),  # Make optional
            twitter: Optional[str] = Form(None, description="team twitter"),  # Make optional
            tiktok: Optional[str] = Form(None, description="team tiktok"),  # Make optional
            role: str = Form(..., description="team role"),
            address: str = Form(..., description="team address"),
            image: UploadFile = Form(..., description="image description"),
    ):
        self.id = id
        self.name = name
        self.email = email
        self.whatsapp = whatsapp
        self.facebook = facebook
        self.instagram = instagram
        self.twitter = twitter
        self.tiktok = tiktok
        self.role = role
        self.address = address
        self.image = image


class TeamModel(BaseModel):
    id: str
    name: str
    email: str
    whatsapp: str
    facebook: Optional[str]
    instagram: Optional[str]
    twitter: Optional[str]
    tiktok: Optional[str]
    role: str
    image: str
    address: str
    created_at: int
    updated_at: int


class TeamPaginationModel(BaseModel):
    page_number: int
    page_size: int
    total: int
    total_pages: int
    teams: List[TeamModel]
