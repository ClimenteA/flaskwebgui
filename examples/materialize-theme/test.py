import os, time, psutil
import subprocess as sps
from threading import Thread, Event


class FlaskUI:

    def __init__(self, app, host="localhost", port=5000):
    
        self.browser_path = self.find_chrome_linux()
        self.app = app
        self.localhost = "http://{}:{}/".format(host, port)
        self.host = host
        self.port = port
        self.server_thread = Thread(target=self.open_flask)
        self.browser_thread = Thread(target=self.open_flask)
        self.close_server_thread = Thread(target=self.close_server)
        self.BROWSER_PROCESS = None
     
     
    
    def close_server(self):
        """
            If browser process is not running close flask server
        """
        while self.BROWSER_PROCESS.pid in [p.info['pid'] \
                                           for p in psutil.process_iter(attrs=['pid', 'name']) \
                                           if 'chrome' in p.info['name']]:
            time.sleep(2)
        #Kill current python process
        psutil.Process(os.getpid()).kill()


    def find_chrome_linux(self):
        import whichcraft as wch
        chrome_names = ['chromium-browser',
                        'chromium',
                        'google-chrome',
                        'google-chrome-stable']

        for name in chrome_names:
            chrome = wch.which(name)
            if chrome is not None:
                return chrome
        return None


    def open_browser(self):
        self.BROWSER_PROCESS = sps.Popen([self.browser_path, "--start-maximized", '--app={}'.format(self.localhost)],
                    stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)


    def open_flask(self):
        self.app.run(host=self.host, port=self.port)

        
    def run(self):
        self.server_thread.start()
        self.browser_thread.start()
        self.close_server_thread.start()
        
        
        self.server_thread.join()
        self.browser_thread.join()
        self.close_server_thread.join()












from flask import Flask  
from flask import render_template
# from flaskwebgui import FlaskUI

app = Flask(__name__)
ui = FlaskUI(app)


@app.route("/")
def hello():  
    return render_template('index.html')

@app.route("/home", methods=['GET'])
def home(): 
    return "Home"



if __name__ == "__main__":
    ui.run()
   



