from flaskwebgui import FlaskUI
from nicegui import ui


ui.label("Hello Super NiceGUI!")
ui.button("BUTTON", on_click=lambda: ui.notify("button was pressed"))


def start_nicegui(**kwargs):
    ui.run(**kwargs)


if __name__ in {"__main__", "__mp_main__"}:
    DEBUG = False

    if DEBUG:
        ui.run()
    else:
        FlaskUI(
            server=start_nicegui,
            server_kwargs={"dark": True, "reload": False, "show": False, "port": 3000},
            width=800,
            height=600,
        ).run()
