from flask import Flask, request
from flask import render_template
from flaskwebgui import FlaskUI, close_application

app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/home", methods=["GET"])
def home():
    return render_template("some_page.html")


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files["file"]
    f.save(f.filename)

    return render_template("index.html")


@app.route("/close", methods=["GET"])
def close_window():
    close_application()


def start_flask(**server_kwargs):
    app = server_kwargs.pop("app", None)
    server_kwargs.pop("debug", None)

    try:
        import waitress

        waitress.serve(app, **server_kwargs)
    except:
        app.run(**server_kwargs)


if __name__ == "__main__":
    # app.run(debug=True)

    # Default start flask
    FlaskUI(
        app=app,
        server="flask",
        width=800,
        height=600,
        on_startup=lambda: print("helooo"),
        on_shutdown=lambda: print("byee"),
    ).run()

    # Default start flask with custom kwargs

    # FlaskUI(
    #     server="flask",
    #     server_kwargs={
    #         "app": app,
    #         "port": 3002,
    #     },
    #     width=800,
    #     height=600,
    # ).run()

    # Custom start flask

    # def saybye():
    #     print("on_exit bye")

    # FlaskUI(
    #     server=start_flask,
    #     server_kwargs={
    #         "app": app,
    #         "port": 3000,
    #         "threaded": True,
    #     },
    #     width=800,
    #     height=600,
    #     on_shutdown=saybye,
    # ).run()
