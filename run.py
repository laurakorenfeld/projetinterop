from socket import SocketIO

from app import app

app.run(debug = True)
socketio = SocketIO(app)