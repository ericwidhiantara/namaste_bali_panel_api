import os
import uuid
from datetime import datetime

from fastapi import FastAPI, status
from pymongo import MongoClient

from app.handler.http_handler import CustomHttpException
from app.models.users import FormUserModel, FormEditUserModel
from app.utils.helper import save_picture, get_object_url

# Connect to MongoDB
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION = "users"

app = FastAPI()


class UserController:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        self.collection = self.db[COLLECTION]

    async def get_users(self):
        users = self.collection.find()

        items = []
        # Iterate the users
        for user in users:
            user["picture"] = get_object_url(user["picture"])

            # append the user to the items
            items.append(user)

        print("ini users", users)

        return [user for user in items]

    async def get_users_pagination(self, page_number=1, page_size=10, search=None):
        # Calculate the skip value based on page_number and page_size
        skip = (page_number - 1) * page_size

        # Fetch users from the database with pagination
        users = self.collection.find({
            '$or': [
                {'name': {'$regex': search, '$options': 'i'}},
                {'username': {'$regex': search, '$options': 'i'}},
                {'email': {'$regex': search, '$options': 'i'}},
                {'phone': {'$regex': search, '$options': 'i'}},
            ]
        }).skip(skip).limit(page_size).sort('created_at', -1)

        items = []
        # Iterate the users
        for user in users:
            # set the images to the user
            user.pop("_id")
            user["picture"] = get_object_url(user["picture"])

            # append the user to the items
            items.append(user)
            print("items", items)

        # Count total users for pagination
        total_users = self.collection.count_documents({
            '$or': [
                {'first_name': {'$regex': search, '$options': 'i'}},
                {'last_name': {'$regex': search, '$options': 'i'}},
                {'username': {'$regex': search, '$options': 'i'}},
                {'email': {'$regex': search, '$options': 'i'}},
                {'phone': {'$regex': search, '$options': 'i'}},
            ]
        })

        # Calculate total pages
        total_pages = (total_users + page_size - 1) // page_size

        # Prepare JSON response
        response = {
            "page_number": page_number,
            "page_size": page_size,
            "total": total_users,
            "total_pages": total_pages,
            "users": items
        }

        print("ini response", response)
        return response

    async def create_user(self, data: FormUserModel):
        # iterate the data.image
        upload_dir = "/users/" + data.name.lower().replace(" ", "-") + "_"

        picture_path = save_picture(upload_dir, data.picture)
        if picture_path == "File extension not allowed":
            raise CustomHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="File extension not allowed"
            )

        # Create new user
        user = {
            "id": str(uuid.uuid4()),
            "name": data.name,
            "username": data.username,
            "email": data.email,
            "password": data.password,
            "phone": data.phone,
            "picture": picture_path,
            "created_at": int(datetime.now().timestamp()),
            "updated_at": int(datetime.now().timestamp()),
            "is_active": True
        }
        # Insert user into MongoDB
        self.collection.insert_one(user)

        # set item from user
        item = user

        return item

    async def edit_user(self, data: FormEditUserModel):

        item = self.collection.find_one({"id": data.id})
        if not item:
            raise CustomHttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="User not found"
            )

        upload_dir = "/users/" + data.name.lower().replace(" ", "-")

        # Save picture
        picture_path = save_picture(upload_dir, data.picture)
        if picture_path == "File extension not allowed":
            raise CustomHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="File extension not allowed"
            )

        # Create new user
        user = {
            "name": data.name if data.name else item["name"],
            "username": data.username if data.username else item["username"],
            "email": data.email if data.email else item["email"],
            "phone": data.phone if data.phone else item["phone"],
            "picture": picture_path if picture_path else item["picture"],
            "created_at": int(datetime.now().timestamp()),
            "updated_at": int(datetime.now().timestamp()),
        }

        print("ini user", user)
        # Update user into MongoDB
        self.collection.update_one({"id": data.id}, {"$set": user})
        updated = self.collection.find_one({"id": data.id})

        # set item from updated data
        item = updated

        return item

    async def delete_user(self, user_id: str):

        item = self.collection.find_one({"id": user_id})
        if not item:
            raise CustomHttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="User not found"
            )

        # Delete user from MongoDB
        self.collection.delete_one({"id": user_id})
        return None
