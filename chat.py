from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from models import MessageModel

from datetime import datetime, timedelta

# Load environment variables from .env file
load_dotenv()

# MongoDB connection settings
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
        message_dict["is_read"] = False
        message_dict["created_at"] = int(datetime.now().timestamp())
        message_dict["updated_at"] = int(datetime.now().timestamp())
       
        self.collection.insert_one(message_dict)

    def get_messages(self, sender: str, recipient: str):
        # Fetch messages between user1 and user2 from the database
        messages = self.collection.find({
            "$or": [
                {"sender_id": sender, "recipient_id": recipient},
                {"sender_id": recipient, "recipient_id": sender}
            ]
        })
        return messages