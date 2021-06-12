from flask import Flask  
from flask import render_template
from flaskwebgui import FlaskUI

app = Flask(__name__)
ui = FlaskUI(app, width=500, height=500) 


@app.route("/")
def hello():  
    return render_template('index.html')

@app.route("/home", methods=['GET'])
def home(): 
    return render_template('some_page.html')


@app.route("/keep-server-alive", methods=['GET'])
def keep_alive():
    FlaskUI.keep_server_running()
    return ""



if __name__ == "__main__":
    ui.run()
   
