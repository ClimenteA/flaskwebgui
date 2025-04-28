from bottle import Bottle, run, static_file, redirect, request, route, response
import os
from typing import Mapping

app = Bottle()

THISDIR = os.path.dirname(__file__)

with app:

    @route(path = '/static/<path:path>') 
    def callback(path):
        print(path)
        return static_file(path, root=os.path.join(THISDIR, "static"))

    @route('/forum', method="GET")  
    def display_forum():
        if isinstance(request.query, Mapping):
            id = request.query["id"]
            response.content_type = 'application/json'
            return f'{{"request_id":"{id}"}}'

    @route(path="/") 
    def hello():
        redirect("static/index.html")
    

if __name__ == "__main__":

    from flaskwebgui import FlaskUI, get_free_port

    port = get_free_port()

    FlaskUI(
        server=run,
        server_kwargs=dict(
            app=app,
            server="wsgiref",
            host="127.0.0.1",
            port=port,
            interval=1,
            reloader=False,
            quiet=False,
            plugins=None,
            debug=None,
            config=None,
        ),
        width=800,
        height=600,
    ).run()
