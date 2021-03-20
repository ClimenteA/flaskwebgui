from http.server import BaseHTTPRequestHandler, HTTPServer

import psutil
import os, time, re
import sys, subprocess as sps
import logging
import tempfile
from threading import Thread
from datetime import datetime


# ports = ['1234','5678','9101']


# popen = sps.Popen(['netstat', '-lpn'], shell=False, stdout=sps.PIPE)
# (data, err) = popen.communicate()

# pattern = "^tcp.*((?:{0})).* (?P[0-9]*)/.*$"
# pattern = pattern.format(')|(?:'.join(ports))
# prog = re.compile(pattern)
# for line in data.split('\n'):
#     match = re.match(prog, line)
#     if match:
#         pid = match.group('pid')
#         sps.Popen(['kill', '-9', pid])


# def get_pids(port):
#     # lsof -i :5000
#     # kill -9 PID

#     command = "lsof -i :%s | awk '{print $2}'" % port
#     pids = sps.check_output(command, shell=True).decode()
#     if not pids: return

#     pids = re.sub(' +', ' ', pids).split('\n')
    
#     for port in ports:
#         pids = set(get_pids(port))
#         command = 'kill -9 {}'.format(' '.join([str(pid) for pid in pids]))
#         os.system(command)


def kill_pids_by_ports(*ports):
    connections = psutil.net_connections()
    for conn in connections:
        open_port = conn.laddr[1]
        if open_port in ports:
            psutil.Process(conn.pid).kill()
            

temp_dir = tempfile.TemporaryDirectory()
keepalive_file = os.path.join(temp_dir.name, 'bo.txt')

server_log = logging.getLogger('BaseHTTPRequestHandler')
log = logging.getLogger('flaskwebgui')


class S(BaseHTTPRequestHandler):

    def log_message(self, format_str, *args):
        """
            Overrides logging in server.py so it doesn't spit out get requests to stdout.
            This allows the caller to filter out what appears on the console.
        """
        server_log.debug(f"{self.address_string()} - {format_str % args}")

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
            return FlaskUI.find_chrome_win()
        elif sys.platform == 'darwin':
            return FlaskUI.find_chrome_mac()
        elif sys.platform.startswith('linux'):
            return FlaskUI.find_chrome_linux()

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def find_chrome_win():
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
            log.exception(last_exception)
            log.error("Failed to detect chrome location from registry")
        else:

            log.debug(f"Chrome path detected as: {chrome_path}")

        return chrome_path

    def open_browser(self):
        """
            Open the browser selected (by default it looks for chrome)
        """

        if self.app_mode:
            launch_options = None
            if self.fullscreen:
                launch_options = ["--start-fullscreen"]
            elif self.maximized:
                launch_options = ["--start-maximized"]
            else:
                launch_options = ["--window-size={},{}".format(self.width, self.height)]

            options = [self.browser_path, "--new-window", '--app={}'.format(self.localhost)]
            options.extend(launch_options)

            log.debug(f"Opening chrome browser with: {options}")
            self.BROWSER_PROCESS = sps.Popen(options,
                                             stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)
        else:
            import webbrowser
            log.debug(f"Opening python web browser")
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

        # Kill current python process
        if os.path.isfile(keepalive_file):
            # bo.txt is used to save timestamp used to check if browser is open
            os.remove(keepalive_file)


        kill_pids_by_ports(self.port, self.port+1)
    
        

