from flaskwebgui import FlaskUI
from djangodesktop.wsgi import application as app


FlaskUI(app).run()