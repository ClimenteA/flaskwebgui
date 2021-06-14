from flaskwebgui import FlaskUI
from main import app, socketio

FlaskUI(app, socketio=socketio, start_server="flask-socketio").run()