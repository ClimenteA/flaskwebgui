# flaskwebgui [![Downloads](https://pepy.tech/badge/flaskwebgui)](https://pepy.tech/project/flaskwebgui)
Create desktop applications with Flask!

### Install

```
pip install flaskwebgui
```
Or download source file [flaskwebgui.py](https://raw.githubusercontent.com/ClimenteA/flaskwebgui/master/src/flaskwebgui.py) and place it where you need. 

### Usage with Flask

Check this [video](https://www.youtube.com/watch?v=dCHmSJQqD_w)! 

```
from flask import Flask
from flaskwebgui import FlaskUI #get the FlaskUI class

app = Flask(__name__)

# Feed it the flask app instance 
ui = FlaskUI(app)

# do your logic as usual in Flask
@app.route("/")
def index():
return "It works!"

# call the 'run' method
ui.run()

```
### Usage with Django

Make a file 'gui.py'(file name not important) next to 'manage.py' file in the django project folder.

Inside 'gui.py' file add these 2 lines of code:

```

from flaskwebgui import FlaskUI #import FlaskUI class

#You can also call the run function on FlaskUI class instantiation

FlaskUI(server='django').run()

```

Next run from your terminal the bellow command:

```
python gui.py
```

### Configurations

Default FlaskUI class parameters:

* **app**, ==> flask class instance (required)

* **width=800** ==> default width 800

* **height=600** ==> default height 600

* **fullscreen=False** ==> start app in fullscreen

* **app_mode=True** ==> by default it will start chrome in app(desktop) mode without address bar

* **browser_path=""**, ==> full path to browser.exe ("C:/browser_folder/chrome.exe" -needed if you want to start a specific browser)
* **server="flask"** ==> the default backend framework is flask (django is suported also), but you can add a function which starts the desired server for your choosed framework (bottle, web2py pyramid etc)

* **host="127.0.0.1"** ==> specify other if needed

* **port=5000** ==> specify other if needed

Should work on windows/linux/mac with no isssues.

If browser is not found, this would be quick fix: `FlaskUI (app, browser_path=r"path/to/chrome.exe")`

### The recommended way of using flaskwebgui

- Download portable [Chromium](https://chromium.woolyss.com/) for the your targeted os
- place the extracted portable app next to "main.py" file,
- flaskwebgui will look for chrome.exe/.app/.sh
In this way when you distribute it, you don't need users to have chrome installed, it will work like a portable app.

Also, during development of your app do that in the normal way you do a Flask app without flaskwebgui. Use flaskwebgui only when you are finished the app(test the app) and ready to deploy.

**flaskwebgui doesn't interfere with your way of doing a flask application** it just helps converting it into a desktop app more easily with pyinstaller or [pyvan](https://github.com/ClimenteA/pyvan)

### Distribution

You can distribute it as a standalone desktop app with pyinstaller or [pyvan](https://github.com/ClimenteA/pyvan).

### Credits
It's a combination of https://github.com/Widdershin/flask-desktop and https://github.com/ChrisKnott/Eel

flaskwebgui just uses threading to start a flask server and the browser in app mode (for chrome).
It has some advantages over flask-desktop because it doesn't use PyQt5, so you won't have any issues regarding licensing and over Eel because you don't need to learn any logic other than Flask.
**Submit any questions issues you have! Fell free to fork it and improve it if you want!**
