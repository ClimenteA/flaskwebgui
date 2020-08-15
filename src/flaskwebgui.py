from http.server import BaseHTTPRequestHandler, HTTPServer

import os, time, signal
import sys, subprocess as sps
import logging
import tempfile
from threading import Thread
from datetime import datetime

temp_dir = tempfile.TemporaryDirectory()
keepalive_file = os.path.join(temp_dir.name, 'bo.txt')

log = logging.getLogger()

class S(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        '''
        Overrides logging in server.py so it doesn't spit out get reauests to stdout.
        This allows the caller to filter out what appears on the console.
        '''
        log.debug(f"{self.address_string()} - f{format % args}")

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))
        with open(keepalive_file, "w") as f:
            f.write(f"{datetime.now()}")
        

class FlaskUI:
    """
        This class opens in 3 threads the browser, the flask server, and a thread which closes the server if GUI is not opened
        
        Described Parameters:

        app,                              ==> flask  class instance 
        width=800                         ==> default width 800 
        height=600                        ==> default height 600
        fullscreen=False,                 ==> start app in fullscreen mode
        maximized=False,                  ==> start app in maximized window
        app_mode=True                     ==> by default it will start the application in chrome app mode
        browser_path="",                  ==> full path to browser.exe ("C:/browser_folder/chrome.exe")
                                              (needed if you want to start a specific browser)
        server="flask"                    ==> the default backend framework is flask, but you can add a function which starts 
                                              the desired server for your choosed framework (django, bottle, web2py pyramid etc)
        host="localhost"                  ==> specify other if needed
        port=5000                         ==> specify other if needed
        socketio                          ==> specify flask-socketio instance if you are using flask with socketio
        on_exit                           ==> specify on-exit function which will be run before closing the app

    """


    def __init__(self, app=None, width=800, height=600, fullscreen=False, maximized=False, app_mode=True,  browser_path="", server="flask", host="127.0.0.1", port=5000, socketio=None, on_exit=None):
        self.flask_app = app
        self.width = str(width)
        self.height= str(height)
        self.fullscreen = fullscreen
        self.maximized = maximized
        self.app_mode = app_mode
        self.browser_path = browser_path if browser_path else self.get_default_chrome_path()  
        self.server = server
        self.host = host
        self.port = port
        self.socketio = socketio
        self.on_exit = on_exit
        self.localhost = "http://{}:{}/".format(host, port) # http://127.0.0.1:5000/
        self.flask_thread = Thread(target=self.run_flask) #daemon doesn't work...
        self.browser_thread = Thread(target=self.open_browser)
        self.close_server_thread = Thread(target=self.close_server)
        self.BROWSER_PROCESS = None
        

    def run(self):
        """
            Start the flask and gui threads instantiated in the constructor func
        """

        self.flask_thread.start()
        self.browser_thread.start()
        self.close_server_thread.start()

        self.browser_thread.join()
        self.flask_thread.join()
        self.close_server_thread.join()

    
    def run_flask(self):
        """
            Run flask or other framework specified
        """

        if isinstance(self.server, str):
            if self.server.lower() == "flask":
                if self.socketio:
                    self.socketio.run(self.flask_app, host=self.host, port=self.port)
                else:
                    self.flask_app.run(host=self.host, port=self.port)

            elif self.server.lower() == "django":
                if sys.platform in ['win32', 'win64']:
                    os.system("python manage.py runserver {}:{}".format(self.host, self.port))
                else:
                    os.system("python3 manage.py runserver {}:{}".format(self.host, self.port))
            else:
                raise Exception("{} must be a function which starts the webframework server!".format(self.server))
        else:
            self.server()


    def get_default_chrome_path(self):
        """
            Credits for get_instance_path, find_chrome_mac, find_chrome_linux, find_chrome_win funcs
            got from: https://github.com/ChrisKnott/Eel/blob/master/eel/chrome.py
        """
        if sys.platform in ['win32', 'win64']:
            return self.find_chrome_win()
        elif sys.platform == 'darwin':
            return self.find_chrome_mac()
        elif sys.platform.startswith('linux'):
            return self.find_chrome_linux()


    def find_chrome_mac(self):
        default_dir = r'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        if os.path.exists(default_dir):
            return default_dir
        # use mdfind ci to locate Chrome in alternate locations and return the first one
        name = 'Google Chrome.app'
        alternate_dirs = [x for x in sps.check_output(["mdfind", name]).decode().split('\n') if x.endswith(name)] 
        if len(alternate_dirs):
            return alternate_dirs[0] + '/Contents/MacOS/Google Chrome'
        return None


    def find_chrome_linux(self):
        try:
            import whichcraft as wch
        except:
            raise Exception("whichcraft module is not installed/found  \
                             please fill browser_path parameter or install whichcraft!")

        chrome_names = ['chromium-browser',
                        'chromium',
                        'google-chrome',
                        'google-chrome-stable']

        for name in chrome_names:
            chrome = wch.which(name)
            if chrome is not None:
                return chrome
        return None


    def find_chrome_win(self):
        import winreg as reg
        reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe'

        for install_type in reg.HKEY_CURRENT_USER, reg.HKEY_LOCAL_MACHINE:
            try:
                reg_key = reg.OpenKey(install_type, reg_path, 0, reg.KEY_READ)
                chrome_path = reg.QueryValue(reg_key, None)
                reg_key.Close()
            except WindowsError:
                chrome_path = None
            else:
                break

        return chrome_path


    def open_browser(self):
        """
            Open the browser selected (by default it looks for chrome)
        """

        if self.app_mode and self.fullscreen:
            self.BROWSER_PROCESS = sps.Popen([self.browser_path, "--new-window", "--start-fullscreen", '--app={}'.format(self.localhost)],
                                                stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)
        elif self.app_mode and self.maximized:
            self.BROWSER_PROCESS = sps.Popen([self.browser_path, "--new-window", "--start-maximized", '--app={}'.format(self.localhost)],
                                                    stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)
        elif self.app_mode:
            self.BROWSER_PROCESS = sps.Popen([self.browser_path, "--new-window", "--window-size={},{}".format(self.width, self.height),
                                                    '--app={}'.format(self.localhost)],
                                                    stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)
        else:
            import webbrowser
            webbrowser.open_new(self.localhost)
   

    def close_server(self):
        """
            If no get request comes from browser on port + 1 
            then after 10 seconds the server will be closed 
        """

        httpd = HTTPServer(('', self.port+1), S)   
        httpd.timeout = 10     

        while True:
        
            httpd.handle_request()

            log.debug("Checking Gui status")
            
            if os.path.isfile(keepalive_file):
                with open(keepalive_file, "r") as f:
                    bo = f.read().splitlines()[0]
                diff = datetime.now() - datetime.strptime(bo, "%Y-%m-%d %H:%M:%S.%f")

                if diff.total_seconds() > 10:
                    log.info("Gui was closed.")
                    break

            log.debug("Gui still open.")
            
            time.sleep(2)


        if self.on_exit:
            self.on_exit()


        #Kill current python process
        if os.path.isfile(keepalive_file):
            #bo.txt is used to save timestamp used to check if browser is open
            os.remove(keepalive_file)

        try:
            import psutil
            psutil.Process(os.getpid()).kill()
        except:
            os.kill(os.getpid(), signal.SIGSTOP) 












