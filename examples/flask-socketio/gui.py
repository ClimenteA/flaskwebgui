from flaskwebgui import FlaskUI
from main import app, socketio

FlaskUI(app, socketio=socketio).run()