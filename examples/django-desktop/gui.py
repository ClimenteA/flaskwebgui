from _flaskwebgui import FlaskUI
from djangodesktop.wsgi import application as app


ui = FlaskUI(app, start_server='django')

ui.run()