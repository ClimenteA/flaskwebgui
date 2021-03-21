from fastapi import FastAPI
from flaskwebgui import FlaskUI

app = FastAPI()
ui = FlaskUI(app)

@app.get("/")
def read_root():
    return {"message": "Works with FastAPI also!"}

if __name__ == "__main__":
    ui.run()
