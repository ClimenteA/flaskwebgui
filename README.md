## Flaskwebgui
  
[![Downloads](https://pepy.tech/badge/flaskwebgui)](https://pepy.tech/project/flaskwebgui)
[![PyPI](https://img.shields.io/pypi/v/flaskwebgui?color=blue)](https://pypi.org/project/flaskwebgui/)

Create desktop applications with Flask/FastAPI/Django!

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Install](#install)
- [Usage with Flask](#usage-with-flask)
- [Usage with Flask-SocketIO](#usage-with-flask-socketio)
- [Usage with FastAPI](#usage-with-fastapi)
- [Usage with Django](#usage-with-django)
- [Close application using a route](#close-application-using-a-route)
- [Prevent users from opening browser console](#prevent-users-from-opening-browser-console)
- [Configurations](#configurations)
- [Advanced Usage](#advanced-usage)
- [Distribution](#distribution)
- [Observations](#observations)
- [Credits](#credits)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


## Install

``` py
pip install flaskwebgui
```
If you are using `conda` checkout [this link](https://github.com/conda-forge/flaskwebgui-feedstock).


## Usage with Flask

Let's say we have the following flask application:
```py
#main.py

from flask import Flask  
from flask import render_template
from flaskwebgui import FlaskUI # import FlaskUI

app = Flask(__name__)


@app.route("/")
def hello():  
    return render_template('index.html')

@app.route("/home", methods=['GET'])
def home(): 
    return render_template('some_page.html')


if __name__ == "__main__":
  # If you are debugging you can do that in the browser:
  # app.run()
  # If you want to view the flaskwebgui window:
  FlaskUI(app=app, server="flask").run()
   
```

Install [`waitress`](https://pypi.org/project/waitress/) for more performance.


## Usage with Flask-SocketIO

Let's say we have the following SocketIO application:
```py
#main.py
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
    FlaskUI(
        app=app,
        socketio=socketio,
        server="flask_socketio",
        width=800,
        height=600,
    ).run()

```

App will be served by `flask_socketio`.


## Usage with FastAPI

Pretty much the same, below you have the `main.py` file:
```py
#main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI
from flaskwebgui import FlaskUI

app = FastAPI()

# Mounting default static files
app.mount("/public", StaticFiles(directory="dist/"))
templates = Jinja2Templates(directory="dist")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request): 
    return templates.TemplateResponse("some_page.html", {"request": request})


if __name__ == "__main__":
    
    FlaskUI(app=app, server="fastapi").run()

```

FastApi will be served by `uvicorn`.  


## Usage with Django

Next to `manage.py` file create a `gui.py` file where you need to import `application` from project's `wsgi.py` file.

```bash
├── project_name
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── gui.py # this 
├── manage.py
```

In `gui.py` file add below code.

```py
#gui.py
from flaskwebgui import FlaskUI
from djangodesktop.wsgi import application as app

if __name__ == "__main__":
    FlaskUI(app=app, server="django").run()

```
Next start the application with:
```py
python gui.py  
```

Install `waitress` for more performance.


## Close application using a route

You can close the application using the `close_application` from flaskwebgui. 

```python

from flaskwebgui import FlaskUI, close_application

# Any python webframework routing here

@app.route("/close", methods=["GET"])
def close_window():
    close_application()

```

And somewhere a link: 

```html

<a href="/close" class="exit" role="button">
    CLOSE
</a>

```


## Prevent users from opening browser console

Add below js script to your index.html file to prevent users from opening the browser console.
You can extend it to prevent other browser specific features.

Native like features are pretty hard to implement because we have access only to javascript.

See [issue 135](https://github.com/ClimenteA/flaskwebgui/issues/135).

```js

<script>

    // Prevent F12 key
    document.onkeydown = function (e) {
        if (e.key === "F12") {
            e.preventDefault();
        }
    };

    // Prevent right-click 
    document.addEventListener("contextmenu", function (e) {
        e.preventDefault();
    });

</script>

```


## Configurations

Default FlaskUI class parameters:

- `server: Union[str, Callable[[Any], None]]`: function which receives `server_kwargs` to start server (see examples folder);
- `server_kwargs: dict = None`: kwargs which will be passed down to `server` function;
- `app: Any = None`: `wsgi` or `asgi` app;
- `port: int = None`: specify port if not a free port will set;
- `width: int = None`: width of the window;
- `height: int = None`: height of the window;
- `fullscreen: bool = True`: start app in fullscreen (maximized);
- `on_startup: Callable = None`: function to before starting the browser and webserver;
- `on_shutdown: Callable = None`: function to after the browser and webserver shutdown;
- `extra_flags: List[str] = None`: list of additional flags for the browser command;
- `browser_path: str = None`: set path to chrome executable or let the defaults do that;
- `browser_command: List[str] = None`: command line with starts chrome in `app` mode;
- `socketio: Any = None`: socketio instance in case of flask_socketio;

Develop your app as you would normally do, add flaskwebgui at the end or for tests.
**flaskwebgui doesn't interfere with your way of doing an application** it just helps converting it into a desktop app more easily with pyinstaller or [pyvan](https://github.com/ClimenteA/pyvan).


## Advanced Usage

You can plug in any python webframework you want just by providing a function to start the server in `server` FlaskUI parameter which will be feed `server_kwargs`.

Example:

```python

# until here is the flask example from above

def start_flask(**server_kwargs):

    app = server_kwargs.pop("app", None)
    server_kwargs.pop("debug", None)

    try:
        import waitress

        waitress.serve(app, **server_kwargs)
    except:
        app.run(**server_kwargs)


if __name__ == "__main__":

    # Custom start flask

    def saybye():
        print("on_exit bye")

    FlaskUI(
        server=start_flask,
        server_kwargs={
            "app": app,
            "port": 3000,
            "threaded": True,
        },
        width=800,
        height=600,
        on_shutdown=saybye,
    ).run()

```
In this way any webframework can be plugged in and the webframework can be started in a more customized manner.

Here is another example with the `nicegui` package:

```python

from flaskwebgui import FlaskUI
from nicegui import ui

ui.label("Hello Super NiceGUI!")
ui.button("BUTTON", on_click=lambda: ui.notify("button was pressed"))

def start_nicegui(**kwargs):
    ui.run(**kwargs)

if __name__ in {"__main__", "__mp_main__"}:
    DEBUG = False

    if DEBUG:
        ui.run()
    else:
        FlaskUI(
            server=start_nicegui,
            server_kwargs={"dark": True, "reload": False, "show": False, "port": 3000},
            width=800,
            height=600,
        ).run()

```

Checkout `examples` for more information.


## Distribution

You can distribute it as a standalone desktop app with **pyinstaller** or [**pyvan**](https://github.com/ClimenteA/pyvan). If pyinstaller failes try pyinstaller version 5.6.2.

```shell
pyinstaller -w -F  main.py
```

After the command finishes move your files (templates, js,css etc) to the `dist` folder created by pyinstaller.

If you want your desktop application to be installed via snap or flatpack (Linux) checkout:
- [cacao-accounting-flatpak](https://github.com/cacao-accounting/cacao-accounting-flatpak);
- [cacao-accounting-snap](https://github.com/cacao-accounting/cacao-accounting-snap);

Made by [William Moreno](https://github.com/williamjmorenor).

## Observations

- Parameters `width`, `height` and maybe `fullscreen` may not work on Mac;
- Window control is limited to width, height, fullscreen;
- Remember the gui is still a browser - pressing F5 will refresh the page + other browser specific things (you can hack it with js though);
- You don't need production level setup with gunicorn etc - you just have one user to serve;
- If you want to debug/reload features - just run it as you would normally do with `app.run(**etc)`, `uvicorn.run(**etc)`, `python manage.py runserver` etc. flaskwebgui does not provide auto-reload you already have it in the webframework you are using;



## Credits
It's a combination of https://github.com/Widdershin/flask-desktop and https://github.com/ChrisKnott/Eel

It has some advantages over flask-desktop because it doesn't use PyQt5, so you won't have any issues regarding licensing and over Eel because you don't need to learn any logic other than Flask/Django/FastAPI/etc.

**Submit any questions/issues you have! Fell free to fork it and improve it!**


