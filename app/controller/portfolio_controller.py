import os
import uuid
from datetime import datetime

from fastapi import FastAPI, status
from pymongo import MongoClient

from app.handler.http_handler import CustomHttpException
from app.models.schemas import FormPortfolioModel, FormEditPortfolioModel, FormDeletePortfolioModel
from app.utils.helper import save_picture, delete_picture

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

    async def get_projects(self):
        projects = self.collection.find()
        print("ini projects", projects)
        return [project for project in projects]

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

    async def edit_project(self, data: FormEditPortfolioModel):

        item = self.collection.find_one({"id": data.id})
        if not item:
            raise CustomHttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Project not found"
            )
        # iterate the data.picture
        uploaded_pictures = []

        if data.images is not None:
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
            "title": data.title if data.title else item["title"],
            "description": data.description if data.description else item["description"],
            "date_started": data.date_started if data.date_started else item["date_started"],
            "date_finished": data.date_finished if data.date_finished else item["date_finished"],
            "images": uploaded_pictures if uploaded_pictures else item["images"],
            "updated_at": int(datetime.now().timestamp()),
        }

        print("ini project", project)
        # Update project into MongoDB
        self.collection.update_one({"id": data.id}, {"$set": project})
        updated = self.collection.find_one({"id": data.id})
        return updated

    async def delete_project(self, data: FormDeletePortfolioModel):

        item = self.collection.find_one({"id": data.id})
        if not item:
            raise CustomHttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Project not found"
            )

        if item["images"] is not None:
            for file in item["images"]:
                res = delete_picture(file)
                if not res:
                    raise CustomHttpException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Failed to delete picture"
                    )

        # Delete project from MongoDB
        self.collection.delete_one({"id": data.id})
        return None
