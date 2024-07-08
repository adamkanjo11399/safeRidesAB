import base64
import socketio
import threading
import time
import cv2

sio = socketio.Client()
camera_enabled = False

SERVER_IP = "192.168.10.213"
SERVER_PORT = "9094"

@sio.on('message')
def on_message(data):
    global camera_enabled
    camera_enabled = data.get("activate_camera")
    print("camera_enabled", camera_enabled)

@sio.event
def connect():
    print('Connection established')
    # Join room after connecting
    sio.emit('join_room', {'room': 'zone_1', 'id': 'camera_1'})
    print('Joined room zone_1')

@sio.event
def disconnect():
    global camera_enabled
    camera_enabled = False
    print('Disconnected from server')
    # Attempt to reconnect
    reconnect()

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

            # Check if connected before sending message
            if sio.connected:
                sio.emit('send_message', {'room': 'zone_1', 'message': data})
            else:
                print("Not connected, cannot send message")

            time.sleep(0.01)  # Sleep for 1/100 seconds
        print("Waiting for train")
        time.sleep(1)

def connect_and_join():
    try:
        sio.connect(f'http://{SERVER_IP}:{SERVER_PORT}')
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(2)
        reconnect()

def reconnect():
    # Reconnect with a delay
    while not sio.connected:
        print("Attempting to reconnect...")
        try:
            sio.connect(f'http://{SERVER_IP}:{SERVER_PORT}')
        except Exception as e:
            print(f"Reconnection failed: {e}")
        time.sleep(5)  # Wait for 5 seconds before retrying

def main():
    # Start connect_and_join function in a separate thread
    connect_thread = threading.Thread(target=connect_and_join)
    connect_thread.start()

    # Start camera function in a separate thread
    camera_thread = threading.Thread(target=camera)
    camera_thread.start()

if __name__ == '__main__':
    main()
