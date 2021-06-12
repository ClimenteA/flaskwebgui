## Create desktop applications with Flask/FastAPI/Django!
  
[![Downloads](https://pepy.tech/badge/flaskwebgui)](https://pepy.tech/project/flaskwebgui)
[![PyPI](https://img.shields.io/pypi/v/flaskwebgui?color=blue)](https://pypi.org/project/flaskwebgui/)

## Install

``` py
pip install flaskwebgui
```

For any framework selected add bellow js code to your app.
Code bellow makes some pooling to the `/keep-server-alive` endpoint and informs flaskwebgui to keep server running while gui is running. Without code bellow server will close after a few seconds.
```js

async function getRequest(url='') {
    const response = await fetch(url, {
      method: 'GET', 
      cache: 'no-cache'
    })
    return response.json()
}
  
document.addEventListener('DOMContentLoaded', function() {

let url = document.location
let route = "/keep-server-alive"
let interval_request = 3 * 1000 //sec

function keep_alive_server(){
    getRequest(url + route)
    .then(data => console.log(data))
}

setInterval(keep_alive_server, interval_request)()

})

```


## Usage with Flask

Let's say we have the following flask application:
```py
#main.py

from flask import Flask  
from flask import render_template
from flaskwebgui import FlaskUI # import FlaskUI

app = Flask(__name__)
ui = FlaskUI(app, width=500, height=500) # add app and parameters


@app.route("/")
def hello():  
    return render_template('index.html')

@app.route("/home", methods=['GET'])
def home(): 
    return render_template('some_page.html')


@app.route("/keep-server-alive", methods=['GET'])
def keep_alive():
    """ This keeps server runnig """
    return FlaskUI.keep_server_running()


if __name__ == "__main__":
    # app.run() for debug
    ui.run()
   
```
Alternatively, next to `main.py` create a file called `gui.py` and add the following contents:

```py
#gui.py

from flaskwebgui import FlaskUI
from main import app

FlaskUI(app, width=600, height=500).run()
```
Next start the application with:
```py
python main.py 
#or
python gui.py #in case you created gui.py 
```
Application will start chrome in app mode, flask will be served by `waitress`.  


## Usage with Flask-SocketIO

Let's say we have the following SocketIO application:
```py
#main.py

from flask import Flask
from flask_socketio import SocketIO
from flaskwebgui import FlaskUI

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@app.route("/")
def index():  
    return {"message": "flask_socketio"}


@app.route("/keep-server-alive", methods=['GET'])
def keep_alive():
    """ This keeps server runnig """
    return FlaskUI.keep_server_running()


if __name__ == '__main__':
    # socketio.run(app) for development
    FlaskUI(app, socketio=socketio).run()   

```
Alternatively, next to `main.py` create a file called `gui.py` and add the following contents:

```py
#gui.py

from flaskwebgui import FlaskUI
from main import app, socketio

FlaskUI(app, socketio=socketio).run()
```
Next start the application with:
```py
python main.py 
#or
python gui.py #in case you created gui.py 
```
Application will start chrome in app mode, flask will be served by `socketio`.  


## Usage with FastAPI

Pretty much the same, bellow you have the `main.py` file:
```py
#main.py

from fastapi import FastAPI
from flaskwebgui import FlaskUI # import FlaskUI

app = FastAPI()
ui = FlaskUI(app) # feed app and parameters

@app.get("/")
def read_root():
    return {"message": "Works with FastAPI also!"}


@app.route("/keep-server-alive", methods=['GET'])
def keep_alive():
    """ This keeps server runnig """
    return FlaskUI.keep_server_running()


if __name__ == "__main__":
    ui.run()

```
Alternatively, next to `main.py` create a file called `gui.py` and add the following contents:

```py
#gui.py

from flaskwebgui import FlaskUI
from main import app

FlaskUI(app, width=600, height=500).run()
```
Next start the application with:
```py
python main.py 
#or
python gui.py #in case you created gui.py 
```
Fastapi will be served by `uvicorn`.  


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

In a app created add `/keep-server-alive` GET endpoint which calls `FlaskUI.keep_server_running()`.


```py
#gui.py

from flaskwebgui import FlaskUI
from project_name.wsgi import application

FlaskUI(application).run()

```
Next start the application with:
```py
python gui.py  
```
Django will be served by `waitress`.  



### Configurations

Default FlaskUI class parameters:

* **app**, ==> app instance

* **width=800** ==> window width default 800

* **height=600** ==> default height 600

* **fullscreen=False** ==> start app in fullscreen (equvalent to pressing `F11` on chrome)

* **maximized=False** ==> start app in maximized window

* **browser_path=None** ==> path to `browser.exe` (absolute path to chrome `C:/browser_folder/chrome.exe`)

* **start_server=None** ==> You can add a function which starts the desired server for your choosed framework (bottle, web2py pyramid etc) or specify one of the supported frameworks: `flask-socketio`, `flask`, `django`, `fastapi`

* **socketio=SocketIO Instance** ==> Flask SocketIO instance (if specified, uses `socketio.run()` instead of `app.run()` for Flask application)

Should work on windows/linux/mac with no isssues.

Develop your app as you would normally do, add flaskwebgui at the end or for tests.
**flaskwebgui doesn't interfere with your way of doing a flask application** it just helps converting it into a desktop app more easily with pyinstaller or [pyvan](https://github.com/ClimenteA/pyvan).

### Distribution

You can distribute it as a standalone desktop app with pyinstaller or [pyvan](https://github.com/ClimenteA/pyvan).

### Credits
It's a combination of https://github.com/Widdershin/flask-desktop and https://github.com/ChrisKnott/Eel

flaskwebgui just uses threading to start a flask server and the browser in app mode (for chrome).
It has some advantages over flask-desktop because it doesn't use PyQt5, so you won't have any issues regarding licensing and over Eel because you don't need to learn any logic other than Flask/Django.

**Submit any questions/issues you have! Fell free to fork it and improve it!**


