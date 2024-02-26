import asyncio
import json

import websockets


async def send_receive_message():
    async with websockets.connect(
            'ws://localhost:8000/ws/191e9135-11d2-4053-85c3-2f7477d001f6') as websocket:
        # Send a message
        await websocket.send(json.dumps({"user_id": "191e9135-11d2-4053-85c3-2f7477d001f6"}))
        print("Online.")

        # Receive a message
        response = await websocket.recv()
        print("Received message:", response)


asyncio.run(send_receive_message())
