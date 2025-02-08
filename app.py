from flask import Flask, render_template, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import os

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Store active users and their rooms
users = {}
# Store room information
rooms = {}

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
