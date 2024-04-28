import os
import uuid
from datetime import datetime

from fastapi import FastAPI, status
from pymongo import MongoClient

from app.handler.http_handler import CustomHttpException
from app.models.orders import FormOrderModel, FormEditOrderModel
from app.utils.helper import save_picture

# Connect to MongoDB
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION = "orders"
USER_COLLECTION = "users"

app = FastAPI()


class OrderController:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        self.collection = self.db[COLLECTION]
        self.user_collection = self.db[USER_COLLECTION]

    async def get_orders(self):
        orders = self.collection.find()

        items = []
        # Iterate the orders
        for order in orders:
            # append the order to the items
            order["user"] = self.user_collection.find_one({"id": order["user_id"]})
            print("ini user order", order["user"])

            items.append(order)

        print("ini orders", orders)

        return [order for order in items]

    async def get_orders_pagination(self, page_number=1, page_size=10, search=None):
        # Calculate the skip value based on page_number and page_size
        skip = (page_number - 1) * page_size

        # Fetch orders from the database with pagination
        orders = self.collection.find({
            '$or': [
                {'customer_name': {'$regex': search, '$options': 'i'}},
                {'customer_email': {'$regex': search, '$options': 'i'}},
                {'customer_address': {'$regex': search, '$options': 'i'}},
                {'customer_phone': {'$regex': search, '$options': 'i'}},
            ]
        }).skip(skip).limit(page_size).sort('created_at', -1)

        items = []
        # Iterate the orders
        for order in orders:
            # set the images to the order
            order.pop("_id")
            order["user"] = self.user_collection.find_one({"id": order["user_id"]})

            # append the order to the items
            items.append(order)
            print("items", items)

        # Count total orders for pagination
        total_orders = self.collection.count_documents({
            '$or': [
                {'customer_name': {'$regex': search, '$options': 'i'}},
                {'customer_email': {'$regex': search, '$options': 'i'}},
                {'customer_address': {'$regex': search, '$options': 'i'}},
                {'customer_phone': {'$regex': search, '$options': 'i'}},
            ]
        })

        # Calculate total pages
        total_pages = (total_orders + page_size - 1) // page_size

        # Prepare JSON response
        response = {
            "page_number": page_number,
            "page_size": page_size,
            "total": total_orders,
            "total_pages": total_pages,
            "orders": items
        }

        print("ini response", response)
        return response

    async def create_order(self, data: FormOrderModel):
        order_id = str(uuid.uuid4())
        picture_path = None
        if data.payment_proof:
            # Save picture
            upload_dir = "/orders/" + "order_" + order_id.lower().replace(" ", "-")

            picture_path = save_picture(upload_dir, data.payment_proof)
            if picture_path == "File extension not allowed":
                raise CustomHttpException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="File extension not allowed"
                )
        # Create new order
        order = {
            "id": order_id,
            "customer_name": data.customer_name,
            "customer_email": data.customer_email,
            "customer_phone": data.customer_phone,
            "customer_country": data.customer_country,
            "customer_address": data.customer_address,
            "total_price": data.total_price,
            "payment_status": data.payment_status,
            "payment_proof": picture_path if picture_path else None,
            "user_id": data.user_id,
            "created_at": int(datetime.now().timestamp()),
            "updated_at": int(datetime.now().timestamp()),
        }
        # Insert order into MongoDB
        self.collection.insert_one(order)

        # set item from order
        item = order
        item["user"] = self.user_collection.find_one({"id": item["user_id"]})

        return item

    async def edit_order(self, data: FormEditOrderModel):

        item = self.collection.find_one({"id": data.id})
        if not item:
            raise CustomHttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Order not found"
            )
        picture_path = None

        if data.payment_proof:
            # Save picture
            upload_dir = "/orders/" + "order_" + data.id.lower().replace(" ", "-")

            picture_path = save_picture(upload_dir, data.payment_proof)
            if picture_path == "File extension not allowed":
                raise CustomHttpException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="File extension not allowed"
                )

        # Create new order
        order = {
            "customer_name": data.customer_name if data.customer_name else item["customer_name"],
            "customer_email": data.customer_email if data.customer_email else item["customer_email"],
            "customer_phone": data.customer_phone if data.customer_phone else item["customer_phone"],
            "customer_country": data.customer_country if data.customer_country else item["customer_country"],
            "customer_address": data.customer_address if data.customer_address else item["customer_address"],
            "total_price": data.total_price if data.total_price else item["total_price"],
            "payment_status": data.payment_status if data.payment_status else item["payment_status"],
            "payment_proof": picture_path if picture_path else item["payment_proof"],
            "user_id": data.user_id if data.user_id else item["user_id"],
            "created_at": int(datetime.now().timestamp()),
            "updated_at": int(datetime.now().timestamp()),
        }

        print("ini order", order)
        # Update order into MongoDB
        self.collection.update_one({"id": data.id}, {"$set": order})
        updated = self.collection.find_one({"id": data.id})

        # set item from updated data
        item = updated
        item["user"] = self.user_collection.find_one({"id": item["user_id"]})

        return item

    async def delete_order(self, order_id: str):

        item = self.collection.find_one({"id": order_id})
        if not item:
            raise CustomHttpException(
                status_code=status.HTTP_404_NOT_FOUND,
                message="Order not found"
            )

        # Delete order from MongoDB
        self.collection.delete_one({"id": order_id})
        return None
