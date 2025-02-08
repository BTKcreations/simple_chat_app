import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, url_for, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
from datetime import datetime

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins="*")

# Store active users and their rooms
users = {}
# Store room information
rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rooms')
def get_rooms():
    print("Reached the rooms route")
    print("rooms    : "+str(rooms))
    room_details = []
    for room_name, members in rooms.items():
        room_details.append({
            'name': room_name,
            'creator': list(rooms[room_name])[0],  # Replace with actual creator logic
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'members': list(members)
        })
    return render_template('rooms.html', rooms=room_details)

@app.route('/rooms/details')
def room_details():
    room_details = []
    for room_name, members in rooms.items():
        room_details.append({
            'name': room_name,
            'creator': 'username_placeholder',  # Replace with actual creator logic
            'timestamp': '2025-02-08T23:59:06+05:30',  # Replace with actual timestamp logic
            'members': list(members)
        })
    return jsonify(room_details)

@socketio.on('connect')
def handle_connect():
    emit('message', {'user': 'System', 'message': 'Welcome to the chat!'})

@socketio.on('join')
def handle_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    users[username] = room
    
    # Initialize room if not exists
    if room not in rooms:
        rooms[room] = set()
    rooms[room].add(username)
    
    # Emit room update to all users in the room
    room_data = {
        'members': list(rooms[room]),
        'count': len(rooms[room])
    }
    emit('room_update', room_data, room=room)
    emit('message', {'user': 'System', 'message': f'{username} has joined the room {room}'}, room=room)

@socketio.on('leave')
def handle_leave(data):
    username = data['username']
    room = users.get(username)
    if room:
        leave_room(room)
        del users[username]
        if room in rooms:
            rooms[room].discard(username)
            if len(rooms[room]) == 0:
                del rooms[room]
            else:
                # Emit room update to remaining users
                room_data = {
                    'members': list(rooms[room]),
                    'count': len(rooms[room])
                }
                emit('room_update', room_data, room=room)
        emit('message', {'user': 'System', 'message': f'{username} has left the room'}, room=room)

@socketio.on('message')
def handle_message(data):
    username = data['username']
    message = data['message']
    room = users.get(username)
    if room:
        emit('message', {'user': username, 'message': message}, room=room)

def create_app():
    return app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, 
                host='0.0.0.0',
                port=port,
                debug=False)
