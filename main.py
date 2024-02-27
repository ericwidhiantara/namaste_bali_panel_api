import json
import time
from typing import List, Dict

from fastapi import FastAPI, HTTPException, Form, WebSocket, WebSocketDisconnect
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

from auth import AuthController
from chat import ChatController
from models import UserModel, MessageModel

app = FastAPI()

auth_handler = AuthController()
chat_controller = ChatController()

connections: List[WebSocket] = []

# Initialize the set to store active users
active_users = []

# Store active connections
active_connections = {}

# Store connected clients
clients: Dict[str, WebSocket] = {}


class MyMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


app.add_middleware(MyMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    clients[client_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            await send_private_message(client_id, data)
    except WebSocketDisconnect:
        del clients[client_id]


async def send_private_message(sender: str, message: str):
    recipient, msg = message.split(":")
    if recipient in clients:
        await clients[recipient].send_text(f"From {sender}: {msg}")
    else:
        print(f"Recipient '{recipient}' not found")


# WebSocket endpoint for chat
@app.websocket("/join/{sender_id}/{recipient_id}")
async def websocket_endpoint_chat(websocket_chat: WebSocket):
    await websocket_chat.accept()
    connections.append(websocket_chat)  # Add the new connection to the list
    print("ini websocket_chat_endpoint", len(connections))
    try:
        while True:
            data = await websocket_chat.receive_text()
            print("Received data:", data)
            json_data = json.loads(data)

            # Extract the sender_id, recipient_id, and message from the received data
            sender_id = json_data.get("sender_id")
            recipient_id = json_data.get("recipient_id")
            message = json_data.get("message")

            if sender_id is not None and recipient_id is not None and message is not None:
                # Example: Save the message to the database
                message_model = MessageModel(sender_id=sender_id, recipient_id=recipient_id, message=message)
                chat_controller.save_message(message_model)

                # Send the new message to the recipient
                await broadcast_message(sender_id, recipient_id, message)
            else:
                print("Invalid message format:", json_data)

    except WebSocketDisconnect:
        connections.remove(websocket_chat)  # Remove the disconnected connection from the list
        # Handle disconnection
        pass


# Function to broadcast message to all connected clients
async def broadcast_message(sender_id: str, recipient_id: str, message: str):
    for connection in connections:
        sender = await auth_handler.get_user_by_id(sender_id)
        sender.pop("_id", None)
        sender.pop("password", None)
        recipient = await auth_handler.get_user_by_id(recipient_id)
        recipient.pop("_id", None)
        recipient.pop("password", None)

        try:
            await connection.send_text(json.dumps({"sender": sender, "recipient": recipient, "message": message}))
        except Exception as e:
            print("Error broadcasting message:", e)


@app.post("/register/")
async def register(email: str = Form(...),
                   first_name: str = Form(...),
                   last_name: str = Form(...),
                   username: str = Form(...),
                   password: str = Form(...),
                   password_confirmation: str = Form(...), ):
    user = UserModel(email=email, first_name=first_name, last_name=last_name, username=username, password=password,
                     password_confirmation=password_confirmation)
    res = await auth_handler.register_user(user, password_confirmation)
    if not res:
        raise HTTPException(status_code=400, detail="User already exists")
    return {"message": "User registered successfully"}


@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    user = await auth_handler.authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    # Remove _id field if present
    user.pop("_id", None)
    user.pop("password", None)

    access_token = auth_handler.create_access_token({"sub": user["email"], "user": user})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users")
async def get_users():
    users = await auth_handler.get_users()
    return users


@app.get("/messages")
async def get_messages(sender_id: str, recipient_id: str):
    messages_old = chat_controller.get_messages(sender_id, recipient_id)

    messages = [item for item in messages_old]

    # Convert ObjectId to string representation for each user
    for message in messages:
        message.pop("_id", None)
        sender_data = await auth_handler.get_user_by_id(message["sender_id"])
        sender_data.pop("_id", None)

        recipient_data = await auth_handler.get_user_by_id(message["recipient_id"])
        recipient_data.pop("_id", None)

        message["sender"] = sender_data
        message["recipient"] = recipient_data
    print("ini messages", messages)
    return messages


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
