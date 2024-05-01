import os
import uuid
from datetime import datetime

from fastapi import FastAPI, status
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
            destination["image"] = get_object_url(destination["image"])

            items.append(destination)

        print("ini destinations", destinations)

        return [destination for destination in items]

    async def get_destinations_pagination(self, page_number=1, page_size=10, search=None):
        # Calculate the skip value based on page_number and page_size
        skip = (page_number - 1) * page_size

        # Fetch destinations from the database with pagination
        destinations = self.collection.find({
            '$or': [
                {'title': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]
        }).skip(skip).limit(page_size).sort('created_at', -1)

        items = []
        # Iterate the destinations
        for destination in destinations:
            # set the images to the destination
            destination.pop("_id")
            destination["image"] = get_object_url(destination["image"])

            # append the destination to the items
            items.append(destination)
            print("items", items)

        # Count total destinations for pagination
        total_destinations = self.collection.count_documents({
            '$or': [
                {'title': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]
        })

        # Calculate total pages
        total_pages = (total_destinations + page_size - 1) // page_size

        # Prepare JSON response
        response = {
            "page_number": page_number,
            "page_size": page_size,
            "total": total_destinations,
            "total_pages": total_pages,
            "destinations": items
        }

        print("ini response", response)
        return response

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
                message="Destination not found"
            )

        picture_path = None

        if data.image:
            # Save picture
            upload_dir = "/destinations/" + data.id.lower().replace(" ", "-")

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
            "image": picture_path if picture_path else item["image"],
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
                message="Destination not found"
            )

        # Delete destination from MongoDB
        self.collection.delete_one({"id": destination_id})
        return None
