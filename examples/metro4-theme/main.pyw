# Needed to run with no-console
import sys, os
if sys.executable.endswith("pythonw.exe"):
  sys.stdout = open(os.devnull, "w");
  sys.stderr = open(os.path.join(os.getenv("TEMP"), "stderr-"+os.path.basename(sys.argv[0])), "w")


from flask import Flask  
from flask import render_template
from flaskwebview import FlaskUI

app = Flask(__name__)
ui = FlaskUI(app, browser_path=r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", executable_name="main.exe", width=500, height=500)


@app.route("/")
def hello():  
    return render_template('index.html')



@app.route("/home", methods=['GET'])
def home(): 
    return "Home"



if __name__ == "__main__":
    ui.run()
   
