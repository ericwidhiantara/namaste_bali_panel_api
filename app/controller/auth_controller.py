import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pymongo import MongoClient

from app.models.schemas import UserAuth, SystemUser, UserOut
from app.utils.deps import get_current_user
from app.utils.utils import (
    create_access_token,
    create_refresh_token,
    verify_password, get_hashed_password
)

load_dotenv()
# Connect to MongoDB
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = "chateo"
USER_COLLECTION = "users"

app = FastAPI()


class AuthController:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        self.collection = self.db[USER_COLLECTION]

    async def register(self, data: UserAuth):
        # Check if user already exists
        if self.collection.find_one({"email": data.email}):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        # Create new user
        user = {
            "id": str(uuid.uuid4()),
            "email": data.email,
            "first_name": data.first_name,
            "last_name": data.last_name,
            "username": data.username,
            "password": get_hashed_password(data.password),
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        return {
            "access_token": create_access_token(dict(user), user["email"]),
            "refresh_token": create_refresh_token(dict(user), user['email']),
        }

    async def get_me(self: SystemUser = Depends(get_current_user)):
        return self

    async def get_users(self, user: UserOut = Depends(get_current_user)):
        print("data user", user.email)
        users = self.collection.find({"email": {"$ne": user.email}}, {'_id': 0})
        print("ini users", users)
        return [user for user in users]

    async def get_user_by_username(self, token: str):
        user = await self.collection.find_one({"username": token})
        return user

    async def get_user_by_id(self, user_id: str):
        user = self.collection.find_one({"id": user_id})
        return user
