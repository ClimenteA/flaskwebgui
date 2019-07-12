# flaskwebgui
#### Create desktop applications with Flask!

<br>

### Install
```
pip install flaskwebgui
```
### Usage
```
from flask import Flask  
from flaskwebgui import FlaskUI #get the FlaskUI class


app = Flask(__name__)

# Feed it the flask app instance (check bellow what param you can add)
ui = FlaskUI(app) 


# do your logic as usual in Flask

@app.route("/")
def index():  
    return "It works!"



# call the 'run' method
ui.run()
 
```
### Configurations

Default FlaskUI class parameters: 

* **app**,                              ==> flask  class instance (required)
* **width=800**                         ==> default width 800 
* **height=600**                        ==> default height 600
* **browser_path=""**,                  ==> full path to browser.exe ("C:/browser_folder/chrome.exe")
                                        (needed if you want to start a specific browser)
* **server="flask"**                    ==> the default backend framework is flask, but you can add a function which starts 
                                        the desired server for your choosed framework (bottle, django, web2py pyramid etc)
* **host="127.0.0.1"**                  ==> specify other if needed
* **port=5000**                         ==> specify other if needed


Should work on windows/linux/mac with no isssues.

If browser is not found, this would be quick fix: `FlaskUI (app, browser_path=r"path/to/chrome.exe")`

### The recommended way of using flaskwebgui

- Download portable [Chromium](https://chromium.woolyss.com/) for the your targeted os

- place the extracted portable app next to "main.py" file, 

- flaskwebgui will look for chrome.exe/.app/.sh

In this way when you distribute it, you don't need users to have chrome installed, it will work like a portable app.
<br>
 Also, during development of your app do that in the normal way you do a Flask app without flaskwebgui. Use flaskwebgui only when you are finished the app(test the app) and ready to deploy.
<br>
**flaskwebgui doesn't interfere with your way of doing a flask application** it just helps converting it into a desktop app more easily with pyinstaller or [pyvan](https://github.com/ClimenteA/pyvan)


### Distribution

You can distribute it as a standalone desktop app with pyinstaller or [pyvan](https://github.com/ClimenteA/pyvan).


### Credits

It's a combination of https://github.com/Widdershin/flask-desktop and https://github.com/ChrisKnott/Eel
<br>
flaskwebgui just uses threading to start a flask server and the browser in app mode (for chrome)
<br>
It has some advantages over flask-desktop because it doesn't use PyQt5, so you won't have any issues regarding licensing and over Eel because you don't need to learn any logic other than Flask.









