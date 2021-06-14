from flask import Flask, render_template
from flask_socketio import SocketIO
from flaskwebgui import FlaskUI


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)



@app.route("/")
def hello():  
    return render_template('index.html')

@app.route("/home", methods=['GET'])
def home(): 
    return render_template('some_page.html')



if __name__ == '__main__':
    # socketio.run(app) for development
    FlaskUI(app, socketio=socketio, start_server="flask-socketio").run()