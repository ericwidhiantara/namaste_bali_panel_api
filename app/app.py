import json
from typing import List, Dict

from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware.cors import CORSMiddleware

from app.controller.auth_controller import AuthController
from app.controller.chat_controller import ChatController
from app.controller.websocket_controller import WebSocketController
from app.models.schemas import UserAuth, TokenSchema, SystemUser, MessageModel, UserOut
from app.utils.deps import get_current_user

connections: List[WebSocket] = []

# Initialize the set to store active users
active_users = []

# Store active connections
active_connections = {}

# Store connected clients
clients: Dict[str, WebSocket] = {}

app = FastAPI()

auth_controller = AuthController()
chat_controller = ChatController()
websocket_controller = WebSocketController()


class WebsocketController:
    pass


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)


@app.get('/', response_class=RedirectResponse, include_in_schema=False)
async def docs():
    return RedirectResponse(url='/docs')


@app.post('/register', summary="Create new user", response_model=UserOut)
async def register(data: UserAuth = Depends()):
    return await auth_controller.register(data)


@app.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await auth_controller.login(form_data)


@app.get('/me', summary='Get details of currently logged in user', response_model=UserOut)
async def get_me(user: SystemUser = Depends(get_current_user)):
    return user


@app.get("/users", summary='Get all users', response_model=List[UserOut])
async def get_users(user: UserOut = Depends(get_current_user)):
    users = await auth_controller.get_users(user)
    for i in users:
        i["last_message"] = await chat_controller.get_last_message(user.id, i["id"])
    return users


@app.get("/messages", summary='Get all messages between the current user and another user',
         response_model=List[MessageModel])
async def get_messages(recipient_id: str, user: SystemUser = Depends(get_current_user)):
    return await chat_controller.get_messages(user.id, recipient_id)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    clients[client_id] = websocket

    try:
        while True:
            data = await websocket.receive_text()
            await websocket_controller.send_private_message(client_id, data, clients)
    except WebSocketDisconnect:
        del clients[client_id]


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
                await websocket_controller.broadcast_message(sender_id, recipient_id, message, connections)
            else:
                print("Invalid message format:", json_data)

    except WebSocketDisconnect:
        connections.remove(websocket_chat)  # Remove the disconnected connection from the list
        # Handle disconnection
        pass
