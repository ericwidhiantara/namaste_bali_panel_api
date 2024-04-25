import os
import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, status, UploadFile, Form
from pymongo import MongoClient

from app.handler.http_handler import CustomHttpException
from app.models.destinations import FormDestinationModel, FormEditDestinationModel
from app.utils.helper import save_picture, get_object_url

# Connect to MongoDB
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION = "destinations"

app = FastAPI()


class DestinationController:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        self.collection = self.db[COLLECTION]

    async def get_destinations(self):
        destinations = self.collection.find()

        items = []
        # Iterate the destinations
        for destination in destinations:
            # append the destination to the items
            items.append(destination)

        print("ini destinations", destinations)

        return [destination for destination in items]

    async def create_destination(self, data: FormDestinationModel):
        # iterate the data.image
        upload_dir = "/destinations/" + data.title.lower().replace(" ", "-")

        # Save picture
        picture_path = save_picture(upload_dir, data.image)
        if picture_path == "File extension not allowed":
            raise CustomHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="File extension not allowed"
            )

        # Create new destination
        destination = {
            "id": str(uuid.uuid4()),
            "title": data.title,
            "slug": data.title.lower().replace(" ", "-"),
            "description": data.description,
            "image": picture_path,
            "created_at": int(datetime.now().timestamp()),
            "updated_at": int(datetime.now().timestamp()),
        }
        # Insert destination into MongoDB
        self.collection.insert_one(destination)

        # set item from destination
        item = destination

        return item

    async def edit_destination(self, data: FormEditDestinationModel):

        item = self.collection.find_one({"id": data.id})
        if not item:
            raise CustomHttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Project not found"
            )

        upload_dir = "/destinations/" + data.title.lower().replace(" ", "-")

        # Save picture
        picture_path = save_picture(upload_dir, data.image)
        if picture_path == "File extension not allowed":
            raise CustomHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="File extension not allowed"
            )

        # Create new destination
        destination = {
            "title": data.title if data.title else item["title"],
            "slug": data.title.lower().replace(" ", "-"),
            "description": data.description if data.description else item["description"],
            "image": picture_path,
            "updated_at": int(datetime.now().timestamp()),
        }

        print("ini destination", destination)
        # Update destination into MongoDB
        self.collection.update_one({"id": data.id}, {"$set": destination})
        updated = self.collection.find_one({"id": data.id})

        # set item from updated data
        item = updated

        return item

    async def delete_destination(self, destination_id: str):

        item = self.collection.find_one({"id": destination_id})
        if not item:
            raise CustomHttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Project not found"
            )

        # Delete destination from MongoDB
        self.collection.delete_one({"id": destination_id})
        return None
