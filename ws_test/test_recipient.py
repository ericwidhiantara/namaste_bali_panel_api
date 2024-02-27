import asyncio

import websockets


async def send_receive_message():
    async with websockets.connect(
            'ws://localhost:8000/join/191e9135-11d2-4053-85c3-2f7477d001f6/cbc48f4b-b00d-47ca-be0a-aa5ca6dc0ce5') as websocket:
        # Send a message
        await websocket.send({
            "sender_id": "191e9135-11d2-4053-85c3-2f7477d001f6",
            "recipient_id": "cbc48f4b-b00d-47ca-be0a-aa5ca6dc0ce5",
            "message": "Hello, WebSocket! I'm a message from recipient."
        })
        print("Message sent.")

        # Receive a message
        response = await websocket.recv()
        print("Received message:", response)


asyncio.run(send_receive_message())
