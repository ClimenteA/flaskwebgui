from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI
from flaskwebgui import FlaskUI


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


def start_fastapi(**kwargs):
    import uvicorn

    uvicorn.run(**kwargs)


if __name__ == "__main__":

    # Default start fastapi

    FlaskUI(
        app=app,
        server="fastapi",
        width=800,
        height=600,
    ).run()

    # Default start fastapi 2 workers

    # FlaskUI(
    #     app="main:app",
    #     server="fastapi",
    #     width=800,
    #     height=600,
    # ).run()

    # Default start fastapi with custom kwargs

    # FlaskUI(
    #     server="fastapi",
    #     server_kwargs={
    #         "app": app,
    #         "port": 3000,
    #         "reload": False,
    #     },
    #     width=800,
    #     height=600,
    # ).run()

    # Custom start fastapi

    # def saybye():
    #     print("on_exit bye")

    # FlaskUI(
    #     server=start_fastapi,
    #     server_kwargs={
    #         "app": "main:app",
    #         "port": 3000,
    #         "reload": True,
    #     },
    #     width=800,
    #     height=600,
    #     on_shutdown=saybye,
    # ).run()
