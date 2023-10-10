import os
import time
import signal
import psutil
import tempfile
import platform
import subprocess
import socketserver
import multiprocessing
from multiprocessing import Process
from threading import Thread
from dataclasses import dataclass
from typing import Callable, Any, List, Union, Dict
from contextlib import suppress


OPERATING_SYSTEM = platform.system().lower()
PY = "python3" if OPERATING_SYSTEM in ["linux", "darwin"] else "python"


def get_free_port():
    with socketserver.TCPServer(("localhost", 0), None) as s:
        free_port = s.server_address[1]
    return free_port


def kill_port(port: int):
    for proc in psutil.process_iter():
        try:
            for conns in proc.connections(kind="inet"):
                if conns.laddr.port == port:
                    proc.send_signal(signal.SIGTERM)
        except psutil.AccessDenied:
            continue


def close_application():
    import pyautogui

    sig = signal.SIGKILL
    if os.name == 'nt':
        sig = signal.SIGTERM

    pyautogui.hotkey("ctrl", "w")
    os.kill(os.getpid(), sig)


def find_browser_on_linux():
    paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/microsoft-edge-stable",
        "/usr/bin/microsoft-edge",
        "/usr/bin/brave-browser",
    ]
    for path in paths:
        if os.path.exists(path):
            return path

    for path in paths:
        with suppress(subprocess.CalledProcessError):
            bp = (
                subprocess.check_output(["which", path.split("/")[-1]])
                .decode("utf-8")
                .strip()
            )
            if os.path.exists(bp):
                return bp

    return None


def find_browser_on_mac():
    paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def find_browser_on_windows():
    paths = [
        "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "C:\Program Files\Google\Chrome\Application\chrome.exe",
        "C:\Program Files\BraveSoftware\Brave-Browser\Application\\brave.exe",
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return None


def find_browser():
    if OPERATING_SYSTEM == "windows":
        return find_browser_on_windows()
    if OPERATING_SYSTEM == "linux":
        return find_browser_on_linux()
    if OPERATING_SYSTEM == "darwin":
        return find_browser_on_mac()
    return None


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

        waitress.serve(**server_kwargs)


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
            server_kwargs["app"], port=server_kwargs["port"]
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
    browser_path: str = None
    browser_command: List[str] = None
    socketio: Any = None

    def __post_init__(self):
        self.__keyboard_interrupt = False

        if self.port is None:
            self.port = (
                self.server_kwargs.get("port")
                if self.server_kwargs
                else get_free_port()
            )

        if isinstance(self.server, str):
            default_server = webserver_dispacher[self.server]
            self.server = default_server.server
            self.server_kwargs = self.server_kwargs or default_server.get_server_kwargs(
                app=self.app, port=self.port, flask_socketio=self.socketio
            )

        self.profile_dir = os.path.join(tempfile.gettempdir(), "flaskwebgui")
        self.url = f"http://127.0.0.1:{self.port}"
        self.browser_path = self.browser_path or find_browser()
        self.browser_command = self.browser_command or self.get_browser_command()

        if not self.browser_path:
            print("path to chrome not found")
            self.browser_command = [PY, "-m", "webbrowser", "-n", self.url]

    def get_browser_command(self):
        flags = [
            self.browser_path,
            f"--user-data-dir={self.profile_dir}",
            "--new-window",
            "--no-first-run",
        ]

        if self.width and self.height:
            flags.extend([f"--window-size={self.width},{self.height}"])
        elif self.fullscreen:
            flags.extend(["--start-maximized"])

        flags.extend([f"--app={self.url}"])

        return flags

    def start_browser(self, server_process: Union[Thread, Process]):
        print("Command:", " ".join(self.browser_command))
        subprocess.run(self.browser_command)

        if self.browser_path is None:
            while self.__keyboard_interrupt is False:
                time.sleep(1)

        if isinstance(server_process, Process):
            if self.on_shutdown is not None:
                self.on_shutdown()
            server_process.kill()
        else:
            if self.on_shutdown is not None:
                self.on_shutdown()
            kill_port(self.port)

    def run(self):
        if self.on_startup is not None:
            self.on_startup()

        if OPERATING_SYSTEM == "darwin":
            multiprocessing.set_start_method("fork")
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
            print("Stopped")

        return server_process, browser_thread
