import base64
import socketio
import requests
import threading
import time
import cv2
import config

sio = socketio.Client()
camera_enabled = False

SERVER_IP = "192.168.240.163"
SERVER_PORT = "9094" 

@sio.on('message')
def on_message(data):
    global camera_enabled
    camera_enabled = data.get("activate_camera")
        
def camera():
    
    video_stream = cv2.VideoCapture(0)
    width = int(video_stream.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Video width: {width}, height: {height}")
    
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
            sio.emit('send_message', {'room': 'zone_1', 'message': data})
    
            sio.sleep(1/100)
        print("Waiting for train")
        sio.sleep(1)

def connect_and_join():
    try:
        sio.connect(f'http://{SERVER_IP}:{SERVER_PORT}')
        print('Connected to server.')

        # Example join room event
        sio.emit('join_room', {'room': 'zone_1', 'token': 'valid_token_1'})
        print('Joined room1')
        
        sio.wait()  # Keep the client running to receive messages

    except Exception as e:
        print(f"Error: {e}")

def main():
    # Start connect_and_join function in a separate thread
    connect_thread = threading.Thread(target=connect_and_join)
    connect_thread.start()
    
    # Start camera function in a separate thread
    camera_thread = threading.Thread(target=camera)
    camera_thread.start()

if __name__ == '__main__':
    main()
