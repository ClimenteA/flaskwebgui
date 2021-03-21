import psutil
import os, time
import sys, subprocess as sps
import logging
import tempfile
from concurrent.futures import ThreadPoolExecutor
from inspect import isfunction


app_dir_fastapi = ['__call__', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_debug', 'add_api_route', 'add_api_websocket_route', 'add_event_handler', 'add_exception_handler', 'add_middleware', 'add_route', 'add_websocket_route', 'api_route', 'build_middleware_stack', 'debug', 'delete', 'dependency_overrides', 'description', 'docs_url', 'exception_handler', 'exception_handlers', 'extra', 'get', 'head', 'host', 'include_router', 'middleware', 'middleware_stack', 'mount', 'on_event', 'openapi', 'openapi_schema', 'openapi_tags', 'openapi_url', 'openapi_version', 'options', 'patch', 'post', 'put', 'redoc_url', 'root_path', 'root_path_in_servers', 'route', 'router', 'routes', 'servers', 'setup', 'state', 'swagger_ui_init_oauth', 'swagger_ui_oauth2_redirect_url', 'title', 'trace', 'url_path_for', 'user_middleware', 'version', 'websocket', 'websocket_route']
app_dir_flask = ['__call__', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_before_request_lock', '_blueprint_order', '_find_error_handler', '_get_exc_class_and_code', '_got_first_request', '_register_error_handler', '_static_folder', '_static_url_path', 'add_template_filter', 'add_template_global', 'add_template_test', 'add_url_rule', 'after_request', 'after_request_funcs', 'app_context', 'app_ctx_globals_class', 'auto_find_instance_path', 'before_first_request', 'before_first_request_funcs', 'before_request', 'before_request_funcs', 'blueprints', 'cli', 'config', 'config_class', 'context_processor', 'create_global_jinja_loader', 'create_jinja_environment', 'create_url_adapter', 'debug', 'default_config', 'dispatch_request', 'do_teardown_appcontext', 'do_teardown_request', 'endpoint', 'env', 'error_handler_spec', 'errorhandler', 'extensions', 'finalize_request', 'full_dispatch_request', 'get_send_file_max_age', 'got_first_request', 'handle_exception', 'handle_http_exception', 'handle_url_build_error', 'handle_user_exception', 'has_static_folder', 'import_name', 'inject_url_defaults', 'instance_path', 'iter_blueprints', 'jinja_env', 'jinja_environment', 'jinja_loader', 'jinja_options', 'json_decoder', 'json_encoder', 'log_exception', 'logger', 'make_config', 'make_default_options_response', 'make_null_session', 'make_response', 'make_shell_context', 'name', 'open_instance_resource', 'open_resource', 'open_session', 'permanent_session_lifetime', 'preprocess_request', 'preserve_context_on_exception', 'process_response', 'propagate_exceptions', 'raise_routing_exception', 'register_blueprint', 'register_error_handler', 'request_class', 'request_context', 'response_class', 'root_path', 'route', 'run', 'save_session', 'secret_key', 'select_jinja_autoescape', 'send_file_max_age_default', 'send_static_file', 'session_cookie_name', 'session_interface', 'shell_context_processor', 'shell_context_processors', 'should_ignore_error', 'static_folder', 'static_url_path', 'subdomain_matching', 'teardown_appcontext', 'teardown_appcontext_funcs', 'teardown_request', 'teardown_request_funcs', 'template_context_processors', 'template_filter', 'template_folder', 'template_global', 'template_test', 'templates_auto_reload', 'test_cli_runner', 'test_cli_runner_class', 'test_client', 'test_client_class', 'test_request_context', 'testing', 'trap_http_exception', 'try_trigger_before_first_request_functions', 'update_template_context', 'url_build_error_handlers', 'url_default_functions', 'url_defaults', 'url_map', 'url_map_class', 'url_rule_class', 'url_value_preprocessor', 'url_value_preprocessors', 'use_x_sendfile', 'view_functions', 'wsgi_app']
app_dir_django = ['__call__', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_exception_middleware', '_get_response', '_get_response_async', '_middleware_chain', '_template_response_middleware', '_view_middleware', 'adapt_method_mode', 'check_response', 'get_response', 'get_response_async', 'load_middleware', 'make_view_atomic', 'process_exception_by_middleware', 'request_class', 'resolve_request']        


class FlaskUI:
    """
        This class opens in 3 threads the browser, the flask start_server, and a thread which closes the start_server if GUI is not opened
        
        Described Parameters:

        app,                              ==> flask  class instance 
        width=800                         ==> default width 800 
        height=600                        ==> default height 600
        fullscreen=False,                 ==> start app in fullscreen mode
        maximized=False,                  ==> start app in maximized window
        app_mode=True                     ==> by default it will start the application in chrome app mode
        browser_path="",                  ==> full path to browser.exe ("C:/browser_folder/chrome.exe")
                                              (needed if you want to start a specific browser)
        start_server="flask"                    ==> the default backend framework is flask, but you can add a function which starts 
                                              the desired start_server for your choosed framework (django, bottle, web2py pyramid etc)
        host="localhost"                  ==> specify other if needed
        port=5000                         ==> specify other if needed
        socketio                          ==> specify flask-socketio instance if you are using flask with socketio
        on_exit                           ==> specify on-exit function which will be run before closing the app

    """

    def __init__(self, 
        app=None, 
        width=800, 
        height=600, 
        maximized=False, 
        fullscreen=False, 
        browser_path="", 
        app_mode=True,  
        start_server="flask", 
        host="127.0.0.1", 
        port=5000, 
        socketio=None,
        on_exit=None
        ):
        self.app = app
        self.width = str(width)
        self.height= str(height)
        self.fullscreen = fullscreen
        self.maximized = maximized
        self.app_mode = app_mode
        self.browser_path = browser_path if browser_path else self.get_default_chrome_path()  
        self.start_server = start_server
        self.host = host
        self.port = port
        self.socketio = socketio
        self.on_exit = on_exit
        self.localhost = "http://{}:{}/".format(host, port) # http://127.0.0.1:5000/
        self.BROWSER_PROCESS = None
        self.frameworks = ["flask-socketio", "flask", "django", "fastapi"]

        if sorted(dir(self.app)) == sorted(app_dir_fastapi):
            self.start_server="fastapi"
        if sorted(dir(self.app)) == sorted(app_dir_flask):
            self.start_server="flask"
        if sorted(dir(self.app)) == sorted(app_dir_django):
            self.start_server="django"
            
        

    def run(self):
        """
            Start the flask and gui threads instantiated in the constructor func
        """
        with ThreadPoolExecutor() as tex:
            tex.submit(self.run_web_start_server)
            tex.submit(self.open_browser)
            tex.submit(self.keep_alive_web_start_server)


    def run_web_start_server(self):
        """
            Run flask or other framework specified
        """

        if isfunction(self.start_server):
            self.start_server()

        if self.start_server not in self.frameworks:
            raise Exception(f"'start_server'({self.start_server}) not in {','.join(self.frameworks)} and also not a function which starts the webframework")

        logging.warning(f"Detected webframework {self.start_server}")

        if self.start_server == "flask-socketio":
            self.socketio.run(self.app, host=self.host, port=self.port)
    
        elif self.start_server == "flask":
            if self.app: 
                import waitress
                waitress.serve(self.app, host=self.host, port=self.port)
            else:
                os.system(f"waitress-serve --host={self.host} --port={self.port} main:app")

        elif self.start_server == "fastapi": 
            if self.app:
                import uvicorn
                uvicorn.run(self.app, host=self.host, port=self.port, log_level="info")
            else:
                os.system(f"uvicorn --host {self.host} --port {self.port} main:app")

        elif self.start_server == "django":
            if self.app:
                import waitress
                waitress.serve(self.app, host=self.host, port=self.port)
            else:
                contents = os.listdir(os.getcwd())
                for content in contents:
                    if os.path.isdir(content):
                        files = os.listdir(content)
                        if 'wsgi.py' in files:
                            break    
                django_project = os.path.basename(content)  
                os.system(f"waitress-serve --host={self.host} --port={self.port} {django_project}.wsgi:application")
            
    

    def get_default_chrome_path(self):
        """
            Credits for get_instance_path, find_chrome_mac, find_chrome_linux, find_chrome_win funcs
            got from: https://github.com/ChrisKnott/Eel/blob/master/eel/chrome.py
        """
        if sys.platform in ['win32', 'win64']:
            return FlaskUI.find_chrome_win()
        elif sys.platform in ['darwin']:
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
            logging.exception(last_exception)
            logging.error("Failed to detect chrome location from registry")
        else:
            logging.debug(f"Chrome path detected as: {chrome_path}")

        return chrome_path

    def open_browser(self):
        """
            Open the browser selected (by default it looks for chrome)
            # https://peter.sh/experiments/chromium-command-line-switches/
        """

        temp_profile_dir = os.path.join(tempfile.gettempdir(), "flaskwebgui")
        
        if self.app_mode:
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
                '--no-sandbox',
                "--no-first-run",
                # "--window-position=0,0"
                ] + launch_options + [f'--app={self.localhost}']


            # logging.warning(options)
            
            self.BROWSER_PROCESS = sps.Popen(options, stdout=sps.PIPE, stderr=sps.PIPE, stdin=sps.PIPE)

        else:
            import webbrowser
            webbrowser.open_new(self.localhost)


    @staticmethod
    def kill_pids_by_ports(*ports):
        connections = psutil.net_connections()
        for conn in connections:
            open_port = conn.laddr[1]
            if open_port in ports:
                psutil.Process(conn.pid).kill()


    def keep_alive_web_start_server(self):

        while 'pid' not in dir(self.BROWSER_PROCESS):
            time.sleep(1)

        while True:
            pid_running = psutil.pid_exists(self.BROWSER_PROCESS.pid)
            pid_memory_usage = psutil.Process(self.BROWSER_PROCESS.pid).memory_percent()
            
            if (
                pid_running == False
                or 
                pid_memory_usage == 0
            ): break

            time.sleep(5)
            
        logging.warning("closing connections...")
        if self.on_exit: self.on_exit()
        FlaskUI.kill_pids_by_ports(self.port)
