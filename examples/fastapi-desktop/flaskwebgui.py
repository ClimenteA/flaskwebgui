import os
import tempfile
import platform
import webbrowser
import subprocess
import socketserver
from dataclasses import dataclass
from threading import Thread
from multiprocessing import Process
from typing import Callable


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
    chrome_path = "C:\Program Files\Google\Chrome\Application\chrome.exe"
    if os.path.exists(chrome_path):
        return chrome_path
    return None


def find_browser():
    system = platform.system().lower()
    if system == "windows":
        return find_browser_on_windows()
    if system == "linux":
        return find_browser_on_linux()
    if system == "darwin":
        return find_browser_on_mac()
    return None


@dataclass
class FlaskUI:
    start_server: Callable[[int], None]
    port: int = None
    fullscreen: bool = True
    width: int = None
    height: int = None
    on_startup: Callable = None
    on_shutdown: Callable = None
    debug: bool = False
    browser_path: str = None

    def __post_init__(self):
        self.browser_path = self.browser_path or find_browser()
        self.profile_dir = os.path.join(tempfile.gettempdir(), "flaskwebgui")
        self.port = self.port or get_free_port()
        self.url = f"http://127.0.0.1:{self.port}"

    def get_browser_startup_flags(self):

        flags = [
            self.browser_path,
            f"--user-data-dir={self.profile_dir}",
            "--new-window",
            "--no-first-run",
        ]

        if self.fullscreen:
            flags.extend(["--start-maximized"])
        if self.width and self.height:
            flags.extend([f"--window-size={self.width},{self.height}"])

        flags.extend([f"--app={self.url}"])

        print("Command:", " ".join(flags))

        return flags

    def start_browser(self, server_process: Process):

        if self.on_startup is not None:
            self.on_startup()

        if not self.browser_path:
            print("path to chrome not found")
            webbrowser.open_new(self.url)
            return

        subprocess.run(self.get_browser_startup_flags())
        server_process.kill()

    def run(self):

        server_process = Process(target=self.start_server, args=(self.port,))
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
