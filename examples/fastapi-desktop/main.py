from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI
from flaskwebgui import FlaskUI
from threading import Thread
from multiprocessing import Process
import time


app = FastAPI()

# Mounting default static files
app.mount("/dist", StaticFiles(directory="dist/"), name="dist")
app.mount("/css", StaticFiles(directory="dist/css"), name="css")
app.mount("/img", StaticFiles(directory="dist/img"), name="img")
app.mount("/js", StaticFiles(directory="dist/js"), name="js")
templates = Jinja2Templates(directory="dist")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("some_page.html", {"request": request})


def start_uvicorn(port: int, debug: bool = False):
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=debug,
    )


if __name__ == "__main__":

    debug = False

    if debug:
        start_uvicorn()
    else:

        def saybye():
            print("on_exit bye")

        FlaskUI(start_server=start_uvicorn, port=3000, on_shutdown=saybye).run()
