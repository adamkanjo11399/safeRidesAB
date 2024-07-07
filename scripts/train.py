import socketio
import pprint
import asyncio
import socketio
from aiohttp import web
import cv2
import base64
import numpy as np
import traceback
import threading
import asyncio

sio = socketio.AsyncClient()

@sio.event
async def message(data):
    image_data = data.get('image')
    if image_data:
        # Decode the base64 string
        image_bytes = base64.b64decode(image_data)
        # Convert binary data to an image
        np_arr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        cv2.imshow(f'Live Stream', frame)
        cv2.waitKey(1)
    else:
        print("No image data received")

async def connect_and_join():
    try:
        await sio.connect('http://localhost:9094')
        print('Connected to server.')

        # Example join room event
        await sio.emit('join_room', {'room': 'zone_1', 'token': 'valid_token_1'})
        
        print('Joined room1')

        await sio.sleep(1) 
        
        data = {
            "activate_camera": True
        }
        
        # Example send message to room
        await sio.emit('send_message', {'room': 'zone_1', 'message': data})
        
        # await sio.sleep(10) 
        
        # data = {
        #     "activate_camera": False
        # }
        
        # await sio.emit('send_message', {'room': 'zone_1', 'message': data})

        await sio.wait()  # Keep the client running to receive messages
    except Exception as e:
        print(f"Error: {e}")

async def main():
    await connect_and_join()

if __name__ == '__main__':
    asyncio.run(main())
