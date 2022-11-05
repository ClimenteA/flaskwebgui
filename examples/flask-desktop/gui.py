from _flaskwebgui import FlaskUI
from main import app

FlaskUI(
    app, 
    width=600, 
    height=500, 
    start_server='flask',
    close_server_on_exit=False
).run()
