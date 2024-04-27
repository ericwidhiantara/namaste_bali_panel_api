import os
from datetime import datetime

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from pymongo import MongoClient

from app.handler.http_handler import CustomHttpException
from app.models.users import TokenPayload, SystemUser
from app.utils.utils import (
    ALGORITHM,
    JWT_SECRET_KEY
)

# Connect to MongoDB
client = MongoClient(os.getenv("MONGODB_URL"))
db = client[os.getenv("DATABASE_NAME")]
users_collection = db["users"]

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT",
    auto_error=False  # This will return None if no token is provided, then we can return custom exception
)


async def get_current_user(token: str = Depends(reuseable_oauth)) -> SystemUser:
    try:
        if token is None:
            raise CustomHttpException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Not authenticated"
            )

        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise CustomHttpException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                message="Token expired"
            )
    except (jwt.JWTError, ValidationError):
        raise CustomHttpException(
            status_code=status.HTTP_403_FORBIDDEN,
            message="Could not validate credentials"
        )

    # Retrieve user from MongoDB
    user = users_collection.find_one({"email": token_data.sub})

    if user is None:
        raise CustomHttpException(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Could not find user"
        )

    return SystemUser(**user)
