from _flaskwebgui import FlaskUI
from main import app

FlaskUI(app, start_server='fastapi').run()
