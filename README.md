# Flaskwebgui
  
[![Downloads](https://pepy.tech/badge/flaskwebgui)](https://pepy.tech/project/flaskwebgui)
[![PyPI](https://img.shields.io/pypi/v/flaskwebgui?color=blue)](https://pypi.org/project/flaskwebgui/)

Create desktop applications with Flask/FastAPI/Django!

## Install

``` py
pip install flaskwebgui
```
If you are using `conda` checkout [this link](https://github.com/conda-forge/flaskwebgui-feedstock).

For any framework selected add below js code to your app.
Code below makes some pooling to the `/flaskwebgui-keep-server-alive` endpoint and informs flaskwebgui to keep server running while gui is running. Without code below server will close after a few seconds.
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
let route = "/flaskwebgui-keep-server-alive"
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
Application will start chrome in app mode, flask will be served by `waitress` if you have it installed. 


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
    FlaskUI(app, socketio=socketio, start_server="flask-socketio").run()

```
Alternatively, next to `main.py` create a file called `gui.py` and add the following contents:

```py
#gui.py

from flaskwebgui import FlaskUI
from main import app, socketio

FlaskUI(app, socketio=socketio, start_server="flask-socketio").run()
```
Next start the application with:
```py
python main.py 
#or
python gui.py #in case you created gui.py 
```
Application will start chrome in app mode, flask will be served by `socketio`.  


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
app.mount("/dist", StaticFiles(directory="dist/"), name="dist")
app.mount("/css", StaticFiles(directory="dist/css"), name="css")
app.mount("/img", StaticFiles(directory="dist/img"), name="img")
app.mount("/js", StaticFiles(directory="dist/js"), name="js")
templates = Jinja2Templates(directory="dist")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request): 
    return templates.TemplateResponse("some_page.html", {"request": request})


if __name__ == "__main__":
    
    def saybye(): print("on_exit bye")

    FlaskUI(app, start_server='fastapi', on_exit=saybye).run()


```
Alternatively, next to `main.py` create a file called `gui.py` and add the following contents:

```py
#gui.py
from flaskwebgui import FlaskUI
from main import app

FlaskUI(app, start_server='fastapi').run()
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

In `gui.py` file add below code.

```py
#gui.py

from flaskwebgui import FlaskUI
from project_name.wsgi import application

ui = FlaskUI(application, start_server='django')
ui.run()

```
Next start the application with:
```py
python gui.py  
```
Django will be served by `waitress` if you have it installed.  

#### TODO: For Django, flaskwebgui doesn't have middleware and keep-alive endpoint implemented. Console will not close after ui window is closed.    


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

**Setting width, height, fullscreen, maximized may not work in some cases.** 
Flags provided on opening chrome are ignored for some reason. 
I couldn't reproduce the issue in order to fix it, feel free to make a pull request for this.

Develop your app as you would normally do, add flaskwebgui at the end or for tests.
**flaskwebgui doesn't interfere with your way of doing a flask application** it just helps converting it into a desktop app more easily with pyinstaller or [pyvan](https://github.com/ClimenteA/pyvan).

### Distribution

You can distribute it as a standalone desktop app with **pyinstaller** or [**pyvan**](https://github.com/ClimenteA/pyvan).

### Credits
It's a combination of https://github.com/Widdershin/flask-desktop and https://github.com/ChrisKnott/Eel

flaskwebgui just uses threading to start a flask server and the browser in app mode (for chrome).
It has some advantages over flask-desktop because it doesn't use PyQt5, so you won't have any issues regarding licensing and over Eel because you don't need to learn any logic other than Flask/Django.

**Submit any questions/issues you have! Fell free to fork it and improve it!**


