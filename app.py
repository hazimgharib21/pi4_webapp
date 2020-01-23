# -*- coding: utf-8 -*-

from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)

from views import index
from websockets import (
    handle_client_connect_event,
)
