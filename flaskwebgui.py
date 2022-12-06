import multiprocessing
import os
import platform
import signal
import socketserver
import subprocess
import tempfile
import time
from dataclasses import dataclass
from multiprocessing import Process
from threading import Thread
from typing import Any, Callable, Dict, List, Union

import psutil

OPERATING_SYSTEM = platform.system().lower()
PY = "python3" if OPERATING_SYSTEM in ["linux", "darwin"] else "python"


def get_free_port() -> int:
    """
    It creates a TCP server on localhost, on a random port, and then returns the port number

    Returns:
      The free port number.
    """

    with socketserver.TCPServer(("localhost", 0), None) as s:
        free_port = s.server_address[1]
    return free_port


def kill_port(port: int) -> None:
    """
    It iterates over all the processes, and for each process, it iterates over all the connections, and
    if the port of the connection matches the port we're looking for, it sends a SIGTERM signal to the
    process

    Args:
      port (int): The port number you want to kill.
    """

    for proc in psutil.process_iter():
        try:
            for conns in proc.connections(kind="inet"):
                if conns.laddr.port == port:
                    proc.send_signal(signal.SIGTERM)
        except psutil.AccessDenied:
            continue


def find_browser_on_linux() -> Union[str, None]:
    """
    If the browser is in the list of paths, return the path. Otherwise, if the browser is in the list of
    paths, return the path. Otherwise, return None

    Returns:
      The path to the browser.
    """

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
        bp = (
            subprocess.check_output(["which", path.split("/")[-1]])
            .decode("utf-8")
            .strip()
        )
        if os.path.exists(bp):
            return bp

    return None


def find_browser_on_mac() -> Union[str, None]:
    """
    If the path to the browser exists, return the path. Otherwise, return None.

    Returns:
      The first path that exists.
    """

    paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    return next((path for path in paths if os.path.exists(path)), None)


def find_browser_on_windows() -> Union[str, None]:
    """
    It returns the first path in the list that exists, or None if none of them exist

    Returns:
      The first path that exists.
    """

    paths = [
        "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "C:\Program Files\Google\Chrome\Application\chrome.exe",
        "C:\Program Files\BraveSoftware\Brave-Browser\Application\\brave.exe",
    ]
    return next((path for path in paths if os.path.exists(path)), None)


def find_browser() -> Union[str, None]:
    """
    If the operating system is Windows, return the result of the function find_browser_on_windows().

    If the operating system is Linux, return the result of the function find_browser_on_linux().

    If the operating system is Mac, return the result of the function find_browser_on_mac().

    If the operating system is none of the above, return None

    Returns:
      The return value is the browser that is found.
    """

    if OPERATING_SYSTEM == "windows":
        return find_browser_on_windows()
    if OPERATING_SYSTEM == "linux":
        return find_browser_on_linux()
    return find_browser_on_mac() if OPERATING_SYSTEM == "darwin" else None


class BaseDefaultServer:
    # > This class is a base class for a default server

    server: Callable
    get_server_kwargs: Callable


class DefaultServerFastApi:
    @staticmethod
    def get_server_kwargs(**kwargs) -> Dict[str, Any]:
        """
        It returns a dictionary with the keys "app" and "port" and the values of the arguments passed to
        the function

        Returns:
          a dictionary with the keys "app" and "port" and the values are the values of the keys "app"
        and "port" in the kwargs dictionary.
        """

        return {"app": kwargs.get("app"), "port": kwargs.get("port")}

    @staticmethod
    def server(**server_kwargs) -> None:
        """
        It starts a server using the uvicorn library
        """

        import uvicorn

        uvicorn.run(**server_kwargs)


class DefaultServerFlask:
    @staticmethod
    def get_server_kwargs(**kwargs) -> Dict[str, Any]:
        """
        It returns a dictionary with the keys "app" and "port" and the values of the arguments passed to
        the function

        Returns:
          A dictionary with the keys "app" and "port"
        """
        return {"app": kwargs.get("app"), "port": kwargs.get("port")}

    @staticmethod
    def server(**server_kwargs) -> None:
        """
        If waitress is installed, use it, otherwise use the built-in Flask server
        """

        app = server_kwargs.pop("app", None)
        server_kwargs.pop("debug", None)

        try:
            import waitress

            waitress.serve(app, **server_kwargs)
        except Exception:
            app.run(**server_kwargs)


class DefaultServerDjango:
    @staticmethod
    def get_server_kwargs(**kwargs) -> Dict[str, Any]:
        """
        It takes a dictionary of keyword arguments, and returns a dictionary of keyword arguments

        Returns:
          A dictionary with the key "app" and the value of the kwargs["app"] and the key "port" and the
        value of kwargs["port"]
        """

        return {"app": kwargs["app"], "port": kwargs["port"]}

    @staticmethod
    def server(**server_kwargs) -> None:
        """
        It starts a WSGI server using the `waitress` package
        """

        import waitress

        waitress.serve(**server_kwargs)


class DefaultServerFlaskSocketIO:
    @staticmethod
    def get_server_kwargs(**kwargs) -> Dict[str, Any]:
        """
        It takes in a dictionary of keyword arguments, and returns a dictionary of keyword arguments

        Returns:
          A dictionary with the keys: app, flask_socketio, port
        """
        return {
            "app": kwargs.get("app"),
            "flask_socketio": kwargs.get("flask_socketio"),
            "port": kwargs.get("port"),
        }

    @staticmethod
    def server(**server_kwargs) -> None:
        """
        This function is a wrapper for the Flask-SocketIO run function
        """
        server_kwargs["flask_socketio"].run(
            server_kwargs["app"], port=server_kwargs["port"]
        )


webserver_dispatcher: Dict[str, BaseDefaultServer] = {
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
        """
        The function is called when the class is instantiated. It sets the port to a random port if no
        port is specified. It also sets the url to the localhost and port. It also sets the
        browser_command to the path of the browser
        """

        self.__keyboard_interrupt: bool = False

        if self.port is None:
            self.port = (
                self.server_kwargs.get("port")
                if self.server_kwargs
                else get_free_port()
            )

        if isinstance(self.server, str):
            default_server = webserver_dispatcher[self.server]
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

    def get_browser_command(self) -> List[str]:
        """
        It returns a list of strings that will be used to launch the browser

        Returns:
          A list of strings.
        """

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

    def start_browser(self, server_process: Union[Thread, Process]) -> None:
        """
        It starts a browser and then kills the server process

        Args:
          server_process (Union[Thread, Process]): Union[Thread, Process]
        """
        print("Command:", " ".join(self.browser_command))
        subprocess.run(self.browser_command)

        if self.browser_path is None:
            while self.__keyboard_interrupt is False:
                time.sleep(1)

        if isinstance(server_process, Process):
            server_process.kill()
        else:
            kill_port(self.port)

    def run(self):
        """
        If the operating system is Mac, then use the multiprocessing module to start the server process.
        Otherwise, use the threading module to start the server process
        """

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

        if self.on_shutdown is not None:
            self.on_shutdown()
