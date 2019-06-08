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

    """

    def __init__(self, app, browser_name="chrome", browser_path="", localhost="http://127.0.0.1:5000"):
        self.flask_app = app
        self.flask_thread = Thread(target=self.run_flask)
        self.browser_thread = Thread(target=self.open_browser)
        self.close_flask_thread = Thread(target=self.close_server)
        self.browser_name = browser_name
        self.browser_path = browser_path
        self.localhost = localhost

    def run(self):
        """
            Start the flask and gui threads instantiated in the constructor func
            Here is the issue...
            If I close the gui/browser the flask server doesn't stop.. 
        """

        self.flask_thread.start()
        self.browser_thread.start()
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
                sps.Popen([browser_path, '--app={}'.format(self.localhost)], stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)

        else:
            print("browser_name = ", self.browser_name)
            print("browser_path = ", self.browser_path)
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


    def kill_python(self):
        """
            Close all python processes
        """
        for proc in psutil.process_iter():
            if proc.name() == "python.exe":
                proc.kill()


    def close_server(self):
        """
            If chrome or firefox process is not running close flask server
        """

        while self.browser_runs():
            time.sleep(1)

        self.kill_python()

        

        
        


