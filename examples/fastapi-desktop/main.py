from fastapi import FastAPI
from flaskwebgui import FlaskUI

app = FastAPI()


def saybye():
    print("on_exit bye")


@app.get("/")
def read_root():
    return {"message": "Works with FastAPI also!"}

if __name__ == "__main__":
    FlaskUI(app, on_exit=saybye).run()
