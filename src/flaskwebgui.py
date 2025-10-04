import os
import shutil
import time
import uuid
import signal
import psutil
import logging
import tempfile
import platform
import webbrowser
import subprocess
import socketserver
import multiprocessing
from multiprocessing import Process
from threading import Thread
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Union


logger = logging.getLogger('flaskwebgui')
if not logger.handlers:
    log_level_str = os.environ.get('FLASKWEBGUI_LOG_LEVEL', 'DEBUG').upper()
    log_level = getattr(logging, log_level_str, logging.WARNING)
    logging.basicConfig(level=log_level, format='[FLASKWEBGUI] %(levelname)s - %(asctime)s - %(message)s')


FLASKWEBGUI_USED_PORT = None
FLASKWEBGUI_BROWSER_PROCESS = None

DEFAULT_BROWSER = webbrowser.get().name
OPERATING_SYSTEM = platform.system().lower()
PY = "python3" if OPERATING_SYSTEM in ["linux", "darwin"] else "python"

try:
    if OPERATING_SYSTEM == "darwin":
        multiprocessing.set_start_method("fork")
except Exception as ex:
    logger.warning(f"Could not set start method 'fork' for mac: {ex}")


linux_browser_paths = [
    r"/usr/bin/google-chrome",
    r"/usr/bin/microsoft-edge",
    r"/usr/bin/brave-browser",
    r"/usr/bin/chromium",
    # Web browsers installed via flatpak portals
    r"/run/host/usr/bin/google-chrome",
    r"/run/host/usr/bin/microsoft-edge",
    r"/run/host/usr/bin/brave-browser",
    r"/run/host/usr/bin/chromium",
    # Web browsers installed via snap
    r"/snap/bin/chromium",
    r"/snap/bin/brave-browser",
    r"/snap/bin/google-chrome",
    r"/snap/bin/microsoft-edge",
]

mac_browser_paths = [
    r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    r"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    r"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]

windows_browser_paths = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
]


def get_free_port():
    with socketserver.TCPServer(("localhost", 0), None) as s:
        free_port = s.server_address[1]
    return free_port


def kill_port(port: int):
    for proc in psutil.process_iter():
        try:
            for conns in proc.net_connections(kind="inet"):
                if conns.laddr.port == port:
                    proc.send_signal(signal.SIGTERM)
        except psutil.AccessDenied:
            continue


def close_application():
    if FLASKWEBGUI_BROWSER_PROCESS is not None:
        FLASKWEBGUI_BROWSER_PROCESS.terminate()

    kill_port(FLASKWEBGUI_USED_PORT)


def find_browser_in_paths(browser_paths: List[str]):

    compatible_browser_path = None
    for path in browser_paths:

        if not os.path.exists(path):
            continue

        if compatible_browser_path is None:
            compatible_browser_path = path

        if DEFAULT_BROWSER in path:
            return path

    return compatible_browser_path


browser_path_dispacher: Dict[str, Callable[[], str]] = {
    "windows": lambda: find_browser_in_paths(windows_browser_paths),
    "linux": lambda: find_browser_in_paths(linux_browser_paths),
    "darwin": lambda: find_browser_in_paths(mac_browser_paths),
}


class BaseDefaultServer:
    server: Callable
    get_server_kwargs: Callable


class DefaultServerFastApi:
    @staticmethod
    def get_server_kwargs(**kwargs):
        server_kwargs = {"app": kwargs.get("app"), "port": kwargs.get("port")}
        return server_kwargs

    @staticmethod
    def server(**server_kwargs):
        import uvicorn

        uvicorn.run(**server_kwargs)


class DefaultServerFlask:
    @staticmethod
    def get_server_kwargs(**kwargs):
        return {"app": kwargs.get("app"), "port": kwargs.get("port")}

    @staticmethod
    def server(**server_kwargs):
        app = server_kwargs.pop("app", None)
        server_kwargs.pop("debug", None)

        try:
            import waitress

            waitress.serve(app, **server_kwargs)
        except:
            app.run(**server_kwargs)


class DefaultServerDjango:
    @staticmethod
    def get_server_kwargs(**kwargs):
        return {"app": kwargs["app"], "port": kwargs["port"]}

    @staticmethod
    def server(**server_kwargs):
        import waitress
        from whitenoise import WhiteNoise

        application = WhiteNoise(server_kwargs["app"])
        server_kwargs.pop("app")

        waitress.serve(application, threads=100, **server_kwargs)


class DefaultServerFlaskSocketIO:
    @staticmethod
    def get_server_kwargs(**kwargs):
        return {
            "app": kwargs.get("app"),
            "flask_socketio": kwargs.get("flask_socketio"),
            "port": kwargs.get("port"),
        }

    @staticmethod
    def server(**server_kwargs):
        server_kwargs["flask_socketio"].run(
            server_kwargs["app"],
            port=server_kwargs["port"],
            allow_unsafe_werkzeug=True  # required for Flask-SocketIO >=5.3.0
        )


webserver_dispacher: Dict[str, BaseDefaultServer] = {
    "fastapi": DefaultServerFastApi,
    "flask": DefaultServerFlask,
    "flask_socketio": DefaultServerFlaskSocketIO,
    "django": DefaultServerDjango,
}


@dataclass
class FlaskUI:
    server: Union[str, Callable[[Any], None]]
    server_kwargs: dict = None
    app: Any = None
    port: int = None
    width: int = None
    height: int = None
    fullscreen: bool = True
    on_startup: Callable = None
    on_shutdown: Callable = None
    extra_flags: List[str] = None
    browser_path: str = None
    browser_command: List[str] = None
    socketio: Any = None
    profile_dir_prefix: str = "flaskwebgui"
    app_mode: bool = True
    browser_pid: int = None
    auto_close: bool = True

    def __post_init__(self):
        self.__keyboard_interrupt = False
        global FLASKWEBGUI_USED_PORT

        if self.port is None:
            self.port = (
                self.server_kwargs.get("port")
                if self.server_kwargs
                else get_free_port()
            )

        FLASKWEBGUI_USED_PORT = self.port

        if isinstance(self.server, str):
            default_server = webserver_dispacher[self.server]
            self.server = default_server.server
            self.server_kwargs = self.server_kwargs or default_server.get_server_kwargs(
                app=self.app, port=self.port, flask_socketio=self.socketio
            )

        self.profile_dir = os.path.join(
            tempfile.gettempdir(), self.profile_dir_prefix + uuid.uuid4().hex
        )
        self.url = f"http://127.0.0.1:{self.port}"

        self.browser_path = (
            self.browser_path or browser_path_dispacher.get(OPERATING_SYSTEM)()
        )
        self.browser_command = self.browser_command or self.get_browser_command()

    def get_browser_command(self):
        # https://peter.sh/experiments/chromium-command-line-switches/

        flags = [
            self.browser_path,
            f"--user-data-dir={self.profile_dir}",
            "--new-window",
            "--no-default-browser-check",
            "--allow-insecure-localhost",
            "--no-first-run",
            "--disable-sync",
        ]
    
        if self.width and self.height and self.app_mode:
            flags.extend([f"--window-size={self.width},{self.height}"])
        elif self.fullscreen:
            flags.extend(["--start-maximized"])

        if self.extra_flags:
            flags = flags + self.extra_flags

        if self.app_mode:
            flags.append(f"--app={self.url}")
        else:
            flags.extend(["--guest", self.url])

        return flags
    
    
    def start_browser(self, server_process: Union[Thread, Process]):
        logger.info("Command:", " ".join(self.browser_command))
        global FLASKWEBGUI_BROWSER_PROCESS

        FLASKWEBGUI_BROWSER_PROCESS = subprocess.Popen(self.browser_command)
        self.browser_pid = FLASKWEBGUI_BROWSER_PROCESS.pid
        FLASKWEBGUI_BROWSER_PROCESS.wait()

        if not self.auto_close:
            return
        
        if self.browser_path is None:
            while self.__keyboard_interrupt is False:
                time.sleep(1)

        if isinstance(server_process, Process):
            if self.on_shutdown is not None:
                self.on_shutdown()
            self.browser_pid = None
            shutil.rmtree(self.profile_dir, ignore_errors=True)
            server_process.kill()
        else:
            if self.on_shutdown is not None:
                self.on_shutdown()
            self.browser_pid = None
            shutil.rmtree(self.profile_dir, ignore_errors=True)
            kill_port(self.port)

    def run(self):
        if self.on_startup is not None:
            self.on_startup()

        if OPERATING_SYSTEM == "darwin":
            server_process = Process(
                target=self.server, kwargs=self.server_kwargs or {}
            )
        else:
            server_process = Thread(target=self.server, kwargs=self.server_kwargs or {})

        browser_thread = Thread(target=self.start_browser, args=(server_process,))

        try:
            server_process.start()
            browser_thread.start()
            server_process.join()
            browser_thread.join()
        except KeyboardInterrupt:
            self.__keyboard_interrupt = True
            logger.info("Stopped")

        return server_process, browser_thread
