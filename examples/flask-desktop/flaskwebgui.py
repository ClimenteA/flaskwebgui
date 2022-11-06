import os
import tempfile
import platform
import subprocess
import socketserver
from dataclasses import dataclass
from threading import Thread
from multiprocessing import Process
from typing import Callable, Any, List, Union, Dict


OPERATING_SYSTEM = platform.system().lower()
PY = "python3" if OPERATING_SYSTEM in ["linux", "darwin"] else "python"


def get_free_port():
    with socketserver.TCPServer(("localhost", 0), None) as s:
        free_port = s.server_address[1]
    return free_port


def find_browser_on_linux():
    chrome_path = "/usr/bin/google-chrome"
    if os.path.exists(chrome_path):
        return chrome_path
    return subprocess.check_output(["which", "google-chrome"]).decode("utf-8").strip()


def find_browser_on_mac():
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(chrome_path):
        return chrome_path
    return None


def find_browser_on_windows():
    edge_path = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if os.path.exists(edge_path):
        return edge_path
    edge_path = "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    if os.path.exists(edge_path):
        return edge_path
    chrome_path = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    if os.path.exists(chrome_path):
        return chrome_path
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
    def get_server_kwargs(app, port: int):
        server_kwargs = {"app": app, "port": port}
        if isinstance(app, str):
            server_kwargs.update({"workers": 2})
        return server_kwargs

    @staticmethod
    def server(**server_kwargs):

        import uvicorn

        uvicorn.run(**server_kwargs)


class DefaultServerFlask:
    @staticmethod
    def get_server_kwargs(app, port: int):
        return {"app": app, "port": port, "threaded": True}

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
    def get_server_kwargs(app, port: int):
        return {"app": app, "workers": 2, "port": port}

    @staticmethod
    def server(**server_kwargs):
        import uvicorn

        uvicorn.run(**server_kwargs)


webserver_dispacher: Dict[str, BaseDefaultServer] = {
    "fastapi": DefaultServerFastApi,
    "flask": DefaultServerFlask,
    "django": DefaultServerDjango,
}


@dataclass
class FlaskUI:
    server: Union[str, Callable[[Any], None]]
    server_kwargs: dict = None
    app: Any = None
    width: int = None
    height: int = None
    fullscreen: bool = True
    on_startup: Callable = None
    on_shutdown: Callable = None
    browser_path: str = None
    browser_command: List[str] = None

    def __post_init__(self):

        self.port = (
            self.server_kwargs.get("port") if self.server_kwargs else get_free_port()
        )

        if isinstance(self.server, str):
            default_server = webserver_dispacher[self.server]
            self.server = default_server.server
            self.server_kwargs = self.server_kwargs or default_server.get_server_kwargs(
                self.app, self.port
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

    def start_browser(self, server_process: Process):

        if self.on_startup is not None:
            self.on_startup()

        print("Command:", " ".join(self.browser_command))
        subprocess.run(self.browser_command)
        server_process.kill()

    def run(self):

        server_process = Process(target=self.server, kwargs=self.server_kwargs)
        browser_thread = Thread(target=self.start_browser, args=(server_process,))

        try:
            server_process.start()
            browser_thread.start()
            server_process.join()
            browser_thread.join()
        except KeyboardInterrupt:
            print("Stopped")

        if self.on_shutdown is not None:
            self.on_shutdown()
