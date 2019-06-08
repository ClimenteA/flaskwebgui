import os, time, psutil
import sys, subprocess as sps

from threading import Thread


class FlaskUI:
    """
        This class opens in 2 threads the browser and the flask server
        
        Described Parameters:

        app,                              ==> flask  class instance
        browser_name="chrome",            ==> name of the browser "chrome" or "firefox"
        browser_path="",                  ==> full path to browser exe, ex: "C:/browser_folder/chrome.exe"
        localhost="http://127.0.0.1:5000" ==> specify other if needed
        executable_name                   ==> the executable "main.py" will be "main.exe" after freezing
        width=800                         ==> default width 800 
        height=600                        ==> default height 600
    """

    def __init__(self, app, browser_name="chrome", browser_path="", localhost="http://127.0.0.1:5000", executable_name="", width=800, height=600):
        self.flask_app = app
        self.flask_thread = Thread(target=self.run_flask)
        self.browser_thread = Thread(target=self.open_browser)
        self.close_flask_thread = Thread(target=self.close_server)
        self.browser_name = browser_name
        self.browser_path = browser_path
        self.localhost = localhost
        self.executable_name = executable_name
        self.width = str(width)
        self.height= str(height)

    def run(self):
        """
            Start the flask and gui threads instantiated in the constructor func
        """

        self.flask_thread.start()
        self.browser_thread.start()
        
        #Wait for the browser to run (1 min)
        count = 0
        while not self.browser_runs():
            time.sleep(1)
            if count > 60:
                break
            count += 1

        self.close_flask_thread.start()

        self.browser_thread.join()
        self.flask_thread.join()
        self.close_flask_thread.join()

    
    def run_flask(self):
        self.flask_app.run()

    
    def find_browser(self):
        """
            Find a path to browser, Chrome, Chromium or Firefox
            Chrome/Chromium is prefered because it has a nice 'app' mode which looks like a desktop app
        """
        import winreg as reg
        reg_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{}.exe'.format(self.browser_name)

        for install_type in reg.HKEY_CURRENT_USER, reg.HKEY_LOCAL_MACHINE:
            try:
                # Look in the windows registry to find browser path
                reg_key = reg.OpenKey(install_type, reg_path, 0, reg.KEY_READ)
                browser_path = reg.QueryValue(reg_key, None)
                reg_key.Close()
            except WindowsError:
                # Look for portable verstion of chrome next to main.py
                if os.path.isfile("chrome/chrome.exe"):
                    browser_path = "chrome/chrome.exe"
                elif os.path.isfile("chrome/bin/chrome.exe"):
                    browser_path = "chrome/bin/chrome.exe"
                elif os.path.isfile(self.browser_path):
                    browser_path = self.browser_path
                else:
                    raise EnvironmentError("Can't find browser! Please specify 'browser_path'")
            else:
                break

        return browser_path


    def open_browser(self):
        """
            Open the browser selected (by default it looks for chrome)
        """

        browser_path = self.find_browser()
        
        if browser_path != "":
            if self.browser_name == "firefox":
                sps.Popen([browser_path, self.localhost], stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)
            elif "chrome.exe" in browser_path:
                sps.Popen([browser_path, '--app={}'.format(self.localhost), "--window-size={},{}".format(self.width, self.height)], stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)
        else:
            raise Exception("Can't open the browser specified!")
    
    def browser_runs(self):
        """
            Check if firefox or chrome is opened
        """
        chrome = [p.info for p in psutil.process_iter(attrs=['pid', 'name']) if 'chrome' in p.info['name']]
        firefox = [p.info for p in psutil.process_iter(attrs=['pid', 'name']) if 'firefox' in p.info['name']]

        if chrome or firefox:
            return True
        else:
            return False


    def kill_service(self):
        """
            Close all python/background processes
        """

        proc_name = "main.exe" if self.executable_name == ""  else self.executable_name

        for proc in psutil.process_iter():
            if proc.name() == proc_name or proc.name() == "python.exe":
                proc.kill()


    def close_server(self):
        """
            If chrome or firefox process is not running close flask server
        """

        while self.browser_runs():
            time.sleep(1)

        self.kill_service()

        

        
        


