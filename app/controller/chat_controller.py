import os
import uuid
from datetime import datetime

from fastapi import FastAPI, Depends
from pymongo import MongoClient

from app.models.schemas import SystemUser, MessageModel
from app.utils.deps import get_current_user

# Connect to MongoDB
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = "chateo"
MESSAGE_COLLECTION = "messages"

app = FastAPI()


class ChatController:
    def __init__(self):
        self.client = MongoClient(MONGODB_URL)
        self.db = self.client[DATABASE_NAME]
        self.collection = self.db[MESSAGE_COLLECTION]

    def save_message(self, message: MessageModel):
        # Convert MessageModel to dictionary before saving to MongoDB
        message_dict = message.dict()
        message_dict["id"] = str(uuid.uuid4())
        message_dict["is_read"] = False
        message_dict["created_at"] = int(datetime.now().timestamp())
        message_dict["updated_at"] = int(datetime.now().timestamp())

        self.collection.insert_one(message_dict)

    def get_messages(self, sender: str, recipient: str, ):
        print("ini sender", sender)

        # Fetch messages between user1 and user2 from the database
        messages_cursor = self.collection.find({
            "$or": [
                {"sender_id": sender, "recipient_id": recipient},
                {"sender_id": recipient, "recipient_id": sender}
            ]
        })
        # Convert MongoDB cursor to list of dictionaries
        messages = [item for item in messages_cursor]

        # Convert ObjectId to string representation for each user
        for message in messages:
            message.pop("_id", None)

        print("ini messages", messages)
        return messages

    async def get_last_message(self, sender, recipient):
        message = self.collection.find_one({"$or": [
            {"sender_id": sender, "recipient_id": recipient},
            {"sender_id": recipient, "recipient_id": sender}
        ], },
            sort=[('timestamp', -1)],
            projection={'_id': 0}
        )

        if message:
            print("ini message bro", message)
            return dict(message)
        else:
            return None

    async def get_me(self: SystemUser = Depends(get_current_user)):
        return self
