import os
import uuid
from datetime import datetime

from fastapi import FastAPI, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pymongo import MongoClient

from app.handler.http_handler import CustomHttpException
from app.models.schemas import FormPortfolioModel, SystemUser
from app.utils.helper import save_picture

# Connect to MongoDB
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")
USER_COLLECTION = "projects"

app = FastAPI()


class PortfolioController:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        self.collection = self.db[USER_COLLECTION]

    async def create_project(self, data: FormPortfolioModel):
        # iterate the data.picture
        uploaded_pictures = []

        for file in data.images:
            res = save_picture(file)
            if res == "File not allowed":
                raise CustomHttpException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="File not allowed"
                )
            uploaded_pictures.append(res)

        # Create new project
        project = {
            "id": str(uuid.uuid4()),
            "title": data.title,
            "description": data.description,
            "date_started": data.date_started,
            "date_finished": data.date_finished,
            "images": uploaded_pictures,
            "created_at": int(datetime.now().timestamp()),
            "updated_at": int(datetime.now().timestamp()),
        }

        # Insert project into MongoDB
        self.collection.insert_one(project)
        return project

    async def get_projects(self):
        projects = self.collection.find()
        print("ini projects", projects)
        return [project for project in projects]
