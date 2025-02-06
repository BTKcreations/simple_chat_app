from flask import Flask, render_template, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import os

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Store active users and their rooms
users = {}

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
    emit('message', {'user': 'System', 'message': f'{username} has joined the room {room}'}, room=room)

@socketio.on('leave')
def handle_leave(data):
    username = data['username']
    room = users.get(username)
    if room:
        leave_room(room)
        del users[username]
        emit('message', {'user': 'System', 'message': f'{username} has left the room'}, room=room)

@socketio.on('message')
def handle_message(data):
    username = data['username']
    message = data['message']
    room = users.get(username)
    if room:
        emit('message', {'user': username, 'message': message}, room=room)

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    # In production, we need to listen on all interfaces
    socketio.run(app, 
                 host='0.0.0.0', 
                 port=port, 
                 debug=False,  # Disable debug mode in production
                 allow_unsafe_werkzeug=True)  # Allow Werkzeug in production
