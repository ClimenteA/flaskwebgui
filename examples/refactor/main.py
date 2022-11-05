from fastapi import FastAPI
from flaskwebgui import FlaskUI

app = FastAPI()


@app.get("/")
def index():
    return {"status": "success"}


def start_uvicorn():
    import uvicorn

    uvicorn.run(
        "main:app",
        port=5000,
        workers=2,
    )


if __name__ == "__main__":

    FlaskUI(start_server=start_uvicorn, port=5000, fullscreen=True).run()
