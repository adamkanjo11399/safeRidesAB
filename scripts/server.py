import asyncio
import socketio
from aiohttp import web
import traceback
import config

# Dictionary to store connected clients and their rooms
connected_clients = {}

# Set of authorized tokens
AUTHORIZED_TOKENS = {"valid_token_1", "valid_token_2"}

# Creates a new Async Socket IO Server
sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)
# Event handlers

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")
    # Remove client from connected_clients dictionary upon disconnection
    if sid in connected_clients:
        del connected_clients[sid]

@sio.event
async def join_room(sid, data):
    room = data['room']
    token = data['token']
    
    if token not in AUTHORIZED_TOKENS:
        await sio.emit('unauthorized', room=sid)
        return
    
    if sid not in connected_clients:
        connected_clients[sid] = set()
    
    if room not in connected_clients[sid]:
        connected_clients[sid].add(room)
        await sio.enter_room(sid, room)
        await sio.emit('joined', room=room)
        print(f"Client {sid} joined room {room}")
    else:
        await sio.emit('already_joined', room=sid)

@sio.event
async def leave_room(sid, data):
    room = data['room']
    
    if room in connected_clients.get(sid, set()):
        connected_clients[sid].remove(room)
        await sio.leave_room(sid, room)
        await sio.emit('left', room=room)
        print(f"Client {sid} left room {room}")
    else:
        await sio.emit('not_in_room', room=sid)

@sio.event
async def send_message(sid, data):
    room = data['room']
    message = data['message']
    
    if room in connected_clients.get(sid, set()):
        await sio.emit('message', message, room=room, skip_sid=sid)
    else:
        await sio.emit('not_in_room', room=sid)


async def run_server():
    while True:
        try:
            await web._run_app(app, port=int(config.SERVER_PORT))
        except Exception:
            print("Server crashed. Restarting...")
            traceback.print_exc()
            await asyncio.sleep(5)  # Wait for a few seconds before restart

if __name__ == '__main__':
    asyncio.run(run_server())
