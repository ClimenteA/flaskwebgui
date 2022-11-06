from flaskwebgui import FlaskUI
from djangodesktop.wsgi import application as app


def start_django(**server_kwargs):

    import waitress

    waitress.serve(**server_kwargs)


if __name__ == "__main__":

    # Default start django

    FlaskUI(
        app=app,
        server="django",
        width=800,
        height=600,
    ).run()

    # Default start django with custom kwargs

    # FlaskUI(
    #     server="django",
    #     server_kwargs={
    #         "app": app,
    #         "port": 3003,
    #     },
    #     width=800,
    #     height=600,
    # ).run()

    # Custom start django

    # def saybye():
    #     print("on_exit bye")

    # FlaskUI(
    #     server=start_django,
    #     server_kwargs={
    #         "app": app,
    #         "port": 3031,
    #     },
    #     width=800,
    #     height=600,
    #     on_shutdown=saybye,
    # ).run()
