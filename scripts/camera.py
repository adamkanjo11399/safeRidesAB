import base64
import socketio
import cv2
import asyncio
import time

sio = socketio.AsyncClient()

camera_enabled = False

@sio.event
async def message(data):
    global camera_enabled
    camera_enabled = data.get("activate_camera")
    
async def camera():
    
    video_stream = cv2.VideoCapture(0)
    video_stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Lower width for faster processing
    video_stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) # Lower height for faster processing
    
    while True:
        global camera_enabled
        while camera_enabled:
            ret, frame = video_stream.read()

            if not ret:
                print("Failed to capture image")
                continue

            # Convert the image to a binary format
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 30])  # Lower quality for smaller size
            image_data = base64.b64encode(buffer).decode('utf-8')

            data = {
                "image": image_data
            }
            
            # Example send message to room
            await sio.emit('send_message', {'room': 'zone_1', 'message': data})
    
            await sio.sleep(1/100)
        await sio.sleep(1)

async def connect_and_join():
    try:
        await sio.connect('http://192.168.240.163:9094')
        print('Connected to server.')
        await sio.sleep(1) 

        # Example join room event
        await sio.emit('join_room', {'room': 'zone_1', 'token': 'valid_token_1'})

        print('Joined room1')

        await sio.sleep(1) 

        await sio.wait()  # Keep the client running to receive messages
        
    except Exception as e:
        print(f"Error: {e}")

async def main():
    tasks = [
        connect_and_join(),
        camera()
    ]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
