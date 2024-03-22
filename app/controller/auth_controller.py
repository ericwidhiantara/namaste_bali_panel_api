import os
import uuid
from datetime import datetime

from fastapi import FastAPI, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pymongo import MongoClient

from app.handler.http_handler import CustomHttpException
from app.models.schemas import FormUserModel, SystemUser
from app.utils.deps import get_current_user
from app.utils.utils import (
    create_access_token,
    create_refresh_token,
    verify_password, get_hashed_password
)

# Connect to MongoDB
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")
USER_COLLECTION = "users"

app = FastAPI()


class AuthController:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        self.collection = self.db[USER_COLLECTION]

    async def register(self, data: FormUserModel):
        # Check if user already exists
        if self.collection.find_one({"email": data.email}):
            raise CustomHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="User with this email already exists"
            )

        if self.collection.find_one({"username": data.username}):
            raise CustomHttpException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="User with this username already exists"
            )

        # Create new user
        user = {
            "id": str(uuid.uuid4()),
            "first_name": data.first_name,
            "last_name": data.last_name,
            "username": data.username,
            "email": data.email,
            "password": get_hashed_password(data.password),
            "phone": data.phone,
            "created_at": int(datetime.now().timestamp()),
            "updated_at": int(datetime.now().timestamp()),
            "is_active": False
        }

        # Insert user into MongoDB
        self.collection.insert_one(user)
        return user

    async def login(self, form_data: OAuth2PasswordRequestForm = Depends()):
        # Check if user exists
        user = self.collection.find_one({"username": form_data.username})
        if user is None or not verify_password(form_data.password, user['password']):
            raise CustomHttpException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Incorrect email or password"
            )
        return {
            "access_token": create_access_token(dict(user), user["email"]),
            "refresh_token": create_refresh_token(dict(user), user['email']),
        }

    async def get_me(self: SystemUser = Depends(get_current_user)):
        return self

    async def get_users(self):
        users = self.collection.find()
        print("ini users", users)
        return [user for user in users]

    async def get_user_by_username(self, token: str):
        user = await self.collection.find_one({"username": token})
        return user

    async def get_user_by_id(self, user_id: str):
        user = self.collection.find_one({"id": user_id})
        return user
