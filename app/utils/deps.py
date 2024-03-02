import os
from datetime import datetime

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from pymongo import MongoClient

from app.models.schemas import TokenPayload, SystemUser
from app.utils.utils import (
    ALGORITHM,
    JWT_SECRET_KEY
)

load_dotenv()
# Connect to MongoDB
client = MongoClient(os.getenv("MONGODB_URL"))  # Update connection string as needed
db = client["chateo"]  # Replace 'your_database_name' with your MongoDB database name
users_collection = db["users"]  # Collection to store users

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)


async def get_current_user(token: str = Depends(reuseable_oauth)) -> SystemUser:
    try:
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Retrieve user from MongoDB
    user = users_collection.find_one({"email": token_data.sub})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )

    return SystemUser(**user)
