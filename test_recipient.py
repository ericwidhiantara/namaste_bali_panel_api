import asyncio
import websockets

async def send_receive_message():
    async with websockets.connect('ws://localhost:8000/ws/65db3db2da62410f4af29338/65db2b91677dac933d47ee10') as websocket:
        # Send a message
        await websocket.send("Hello, WebSocket! I'm a message from recipient.")
        print("Message sent.")

        # Receive a message
        response = await websocket.recv()
        print("Received message:", response)

asyncio.run(send_receive_message())
