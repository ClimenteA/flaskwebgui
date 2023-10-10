from flask import Flask, render_template
from flask_socketio import SocketIO
from flaskwebgui import FlaskUI, close_application


app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/home", methods=["GET"])
def home():
    return render_template("some_page.html")


@app.route("/close", methods=["GET"])
def close_window():
    close_application()


def start_flask_socketio(**server_kwargs):

    server_kwargs["socketio"].run(server_kwargs["app"], port=server_kwargs["port"])


if __name__ == "__main__":

    # Default start flask

    FlaskUI(
        app=app,
        socketio=socketio,
        server="flask_socketio",
        width=800,
        height=600,
    ).run()

    # Default start flask with custom kwargs

    # FlaskUI(
    #     server="flask_socketio",
    #     server_kwargs={
    #         "app": app,
    #         "flask_socketio": socketio,
    #         "port": 3003,
    #     },
    #     width=800,
    #     height=600,
    # ).run()

    # Custom start flask

    # def saybye():
    #     print("on_exit bye")

    # FlaskUI(
    #     server=start_flask_socketio,
    #     server_kwargs={"app": app, "socketio": socketio, "port": 3000},
    #     width=800,
    #     height=600,
    #     on_shutdown=saybye,
    # ).run()
