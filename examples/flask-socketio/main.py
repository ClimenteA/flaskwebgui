from flask import Flask
from flask_socketio import SocketIO
from flaskwebgui import FlaskUI


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route("/")
def index():  
    return {"message": "flask_socketio"}


if __name__ == '__main__':
    # socketio.run(app) for development
    FlaskUI(app, socketio=socketio).run()