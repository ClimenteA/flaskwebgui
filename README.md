# flaskwebgui
Freeze web apps made in Flask as desktop apps with flaskwebgui and pyinstaller 

### Install
```
pip install flaskwebgui
```
### Usage
```
from flask import Flask  
from flaskwebgui import FlaskUI #get the FlaskUI class


app = Flask(__name__)
ui = FlaskUI(app) # Feed it the flask app instance


# do your logic as usual in Flask

@app.route("/")
def index():  
    return "It works!"


ui.run() # call the 'run' method from the FlaskUI instance
 
```
### Configurations

Default FlaskUI class parameters: 

* app - required, flask app instance
* browser_name="chrome" - default it looks for chrome, you can use "firefox", but it doesn't have app mode..
* browser_path="" - default is "", full path to browser exe, ex: "C:/browser_folder/chrome.exe"  
* localhost="http://127.0.0.1:5000" - default url where the browser will go
<br>
You can use a portable version of Chrome!
<br>
Download Chromium portable from -> https://chromium.woolyss.com/
<br>
Place the portable Chromium app next to main.py file.
<br>

### Distribution

```
pyinstaller main.py
pyinstaller --no-console main.py
pyinstaller --onefile --no-console main.py
```

### Credits

It's a combination of https://github.com/Widdershin/flask-desktop and https://github.com/ChrisKnott/Eel
<br>
flaskwebgui just uses threading to start a flask server and the browser in app mode (for chrome)
<br>
It has some advantages over flask-desktop because it doesn't use PyQt5, so you won't have any issues regarding licensing and over Eel because you don't need to learn any logic other than Flask.









