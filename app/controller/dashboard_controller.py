import os
import uuid
from datetime import datetime

from fastapi import FastAPI, status
from pymongo import MongoClient

from app.handler.http_handler import CustomHttpException
from app.models.users import FormUserModel, FormEditUserModel
from app.utils.helper import save_picture, get_object_url
from app.utils.utils import get_hashed_password

# Connect to MongoDB
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")
USER_COLLECTION = "users"
ORDER_COLLECTION = "orders"
TEAM_COLLECTION = "teams"
DESTINATION_COLLECTION = "destinations"

app = FastAPI()


class DashboardController:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        self.user_collection = self.db[USER_COLLECTION]
        self.order_collection = self.db[ORDER_COLLECTION]
        self.team_collection = self.db[TEAM_COLLECTION]
        self.destination_collection = self.db[DESTINATION_COLLECTION]

    async def get_dashboard_data(self):
        total_unpaid = self.order_collection.count_documents({"payment_status": "unpaid"})
        total_paid = self.order_collection.count_documents({"payment_status": "paid"})
        total_canceled = self.order_collection.count_documents({"payment_status": "canceled"})
        total_teams = self.team_collection.count_documents({})
        total_users = self.user_collection.count_documents({})
        total_orders = self.order_collection.count_documents({})
        total_destinations = self.destination_collection.count_documents({})

        response = {
            "total_unpaid": total_unpaid,
            "total_paid": total_paid,
            "total_canceled": total_canceled,
            "total_teams": total_teams,
            "total_users": total_users,
            "total_orders": total_orders,
            "total_destinations": total_destinations
        }

        return response
