from app import app
from flask_socketio import SocketIO, send, emit
socketio = SocketIO(app)
from threading import Thread, Event
from system_info import DynamicData, StaticData, thread

@socketio.on('client_connected')
def handle_client_connect_event(json):
    global thread
    print('received json: {0}'.format(str(json)))
    sd = StaticData()
    sd.run()
    if not thread.isAlive():
        print("Starting Thread")
        thread = DynamicData()
        thread.start()


