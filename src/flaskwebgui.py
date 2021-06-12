__version__ = "0.3.0"

import os
import sys
import time
from datetime import datetime
import logging
import tempfile
import socketserver
import subprocess as sps
from inspect import isfunction
from concurrent.futures import ThreadPoolExecutor



logging.basicConfig(level=logging.INFO, format='flaskwebgui - [%(levelname)s] - %(message)s')

# UTILS

def find_chrome_mac():

    default_dir = r'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    if os.path.exists(default_dir):
        return default_dir

    # use mdfind ci to locate Chrome in alternate locations and return the first one
    name = 'Google Chrome.app'
    alternate_dirs = [x for x in sps.check_output(["mdfind", name]).decode().split('\n') if x.endswith(name)] 
    if len(alternate_dirs):
        return alternate_dirs[0] + '/Contents/MacOS/Google Chrome'
    return None


def find_chrome_linux():
    try:
        import whichcraft as wch
    except Exception as e:
        raise Exception("whichcraft module is not installed/found  \
                            please fill browser_path parameter or install whichcraft!") from e

    chrome_names = ['chromium-browser',
                    'chromium',
                    'google-chrome',
                    'google-chrome-stable']

    for name in chrome_names:
        chrome = wch.which(name)
        if chrome is not None:
            return chrome
    return None



def find_chrome_win():

    #using edge by default since it's build on chromium
    edge_path = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if os.path.exists(edge_path):
        return edge_path

    import winreg as reg
    reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe'

    chrome_path = None
    last_exception = None

    for install_type in reg.HKEY_CURRENT_USER, reg.HKEY_LOCAL_MACHINE:
        try:
            reg_key = reg.OpenKey(install_type, reg_path, 0, reg.KEY_READ)
            chrome_path = reg.QueryValue(reg_key, None)
            reg_key.Close()
        except WindowsError as e:
            last_exception = e
        else:
            if chrome_path and len(chrome_path) > 0:
                break

    # Only log some debug info if we failed completely to find chrome
    if not chrome_path:
        logging.exception(last_exception)
        logging.error("Failed to detect chrome location from registry")
    else:
        logging.info(f"Chrome path detected as: {chrome_path}")

    return chrome_path


def get_default_chrome_path():
    """
        Credits for get_instance_path, find_chrome_mac, find_chrome_linux, find_chrome_win funcs
        got from: https://github.com/ChrisKnott/Eel/blob/master/eel/chrome.py
    """
    if sys.platform in ['win32', 'win64']:
        return find_chrome_win()
    elif sys.platform in ['darwin']:
        return find_chrome_mac()
    elif sys.platform.startswith('linux'):
        return find_chrome_linux()



temp_profile_dir = os.path.join(tempfile.gettempdir(), "flaskwebgui")
keep_gui_alive   = os.path.join(temp_profile_dir, "keep_gui_alive.txt")

def write_timestamp():
    with open(keep_gui_alive, "w") as f:
        f.write(f"{datetime.now()}")


class FlaskUI:

    def __init__(self, 
        app, 
        start_server='flask',
        width=800, 
        height=600, 
        maximized=False, 
        fullscreen=False, 
        browser_path=None, 
        socketio=None,
        on_exit=None,
        idle_interval=5
        ) -> None:

        self.app = app
        self.start_server = str(start_server).lower()
        self.width = str(width)
        self.height= str(height)
        self.fullscreen = fullscreen
        self.maximized = maximized
        self.browser_path = browser_path if browser_path else get_default_chrome_path()  
        self.socketio = socketio
        self.on_exit = on_exit
        self.idle_interval = idle_interval
     
        self.set_url()
     
        self.framework_dispacher = {
            "flask": self.start_flask,
            "flask-socketio": self.start_flask_socketio,
            "django": self.start_django,
            "fastapi": self.start_fastapi
        }

        self.supported_frameworks = list(self.framework_dispacher.keys())


    def run(self):
        """ 
        Starts 2 threads one for webframework server and one for browser gui 
        """
        
        write_timestamp()

        with ThreadPoolExecutor() as tex:
            tex.submit(self.start_webserver)
            tex.submit(self.open_chromium)
            tex.submit(self.stop_webserver)


    def set_url(self):
        with socketserver.TCPServer(("localhost", 0), None) as s:
            free_port = s.server_address[1]
        self.host = '127.0.0.1'
        self.port = free_port
        self.localhost = f"http://{self.host}:{self.port}" 
       

    def start_webserver(self):

        if isfunction(self.start_server):
            self.start_server()

        if self.start_server not in self.supported_frameworks:
            raise Exception(f"'start_server'({self.start_server}) not in {','.join(self.supported_frameworks)} and also not a function which starts the webframework")

        self.framework_dispacher[self.start_server]()


    def start_flask(self):
        import waitress
        waitress.serve(self.app, host=self.host, port=self.port)

    def start_flask_socketio(self):
        self.socketio.run(self.app, host=self.host, port=self.port)

    def start_django(self):
        import waitress
        waitress.serve(self.app, host=self.host, port=self.port)

    def start_fastapi(self):
        import uvicorn
        uvicorn.run(self.app, host=self.host, port=self.port, log_level="info")


    def open_chromium(self):
        """
            Open the browser selected (by default it looks for chrome)
            # https://peter.sh/experiments/chromium-command-line-switches/
        """

        logging.info(f"Opening browser at {self.localhost}")

        if self.browser_path:
            launch_options = None
            if self.fullscreen:
                launch_options = ["--start-fullscreen"]
            elif self.maximized:
                launch_options = ["--start-maximized"]
            else:
                launch_options = [f"--window-size={self.width},{self.height}"]

            options = [
                self.browser_path, 
                f"--user-data-dir={temp_profile_dir}",
                "--new-window", 
                "--no-sandbox",
                "--no-first-run",
                # "--window-position=0,0"
                ] + launch_options + [f'--app={self.localhost}']


            sps.Popen(options, stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)

        else:
            import webbrowser
            webbrowser.open_new(self.localhost)



    def stop_webserver(self):

        while True:

            with open(keep_gui_alive, "r") as f:
                data = f.read().splitlines()[0]
            
            diff = datetime.now() - datetime.strptime(data, "%Y-%m-%d %H:%M:%S.%f")

            if diff.total_seconds() > self.idle_interval:
                logging.info("App closed")
                break
         
            time.sleep(self.idle_interval)
                

        if isfunction(self.on_exit): 
            logging.info(f"Executing {self.on_exit.__name__} function...")
            self.on_exit()

        logging.info("Closing connections...")
        os.kill(os.getpid(), 9)


    @staticmethod
    def keep_server_running():
        write_timestamp()
        return "Ok"

        
