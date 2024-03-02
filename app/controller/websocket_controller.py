import json
from typing import List, Dict

from fastapi import WebSocket, FastAPI

from app.controller.auth_controller import AuthController
from app.controller.chat_controller import ChatController

app = FastAPI()


class WebSocketController:
    def __init__(self):

        self.auth_controller = AuthController()
        self.chat_controller = ChatController()
        # clients = Dict[str, WebSocket] = {}
        # connections = List[WebSocket] = []

    async def send_private_message(self, sender: str, message: str, clients: Dict[str, WebSocket]):
        recipient, msg = message.split(":")
        if recipient in clients:
            await clients[recipient].send_text(f"From {sender}: {msg}")
        else:
            print(f"Recipient '{recipient}' not found")

    # Function to broadcast message to all connected clients
    async def broadcast_message(self, sender_id: str, recipient_id: str, message: str, connections: List[WebSocket]):
        for connection in connections:
            sender = await self.auth_controller.get_user_by_id(sender_id)
            sender.pop("_id", None)
            sender.pop("password", None)
            recipient = await self.auth_controller.get_user_by_id(recipient_id)
            recipient.pop("_id", None)
            recipient.pop("password", None)

            try:
                await connection.send_text(json.dumps({"sender": sender, "recipient": recipient, "message": message}))
            except Exception as e:
                print("Error broadcasting message:", e)
