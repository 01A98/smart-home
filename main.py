from functools import partial
from typing import Optional

from sanic import Sanic
from sanic.worker.loader import AppLoader
from tortoise.contrib.sanic import register_tortoise

from src.logging import *
from src.settings import SETTINGS
from src.views.bulbs import create_view as create_bulbs_view
from src.views.bulbs_id import create_view as create_bulbs_id_view
from src.views.home import create_view as create_home_view
from src.views.more import create_view as create_more_view
from src.views.rooms import create_view as create_rooms_view


def attach_endpoints(app: Sanic):
    create_home_view(app)
    create_bulbs_view(app)
    create_bulbs_id_view(app)
    create_rooms_view(app)
    create_more_view(app)


def serve_static_files(app: Sanic):
    app.static("/public", "./public", name="public", directory_view=True)
    app.static("/assets", "./assets", name="assets", directory_view=True)


def create_app(app_name: str = "smart-home") -> Sanic:
    app = Sanic(app_name)
    attach_endpoints(app)
    serve_static_files(app)
    register_tortoise(
        app,
        db_url=str(SETTINGS.db_url),
        modules={"models": ["src.models"]},
        generate_schemas=True,
    )
    return app


if __name__ == "__main__":
    app_name = "smart-home"
    loader = AppLoader(factory=partial(create_app, app_name))
    app = loader.load()
    app.prepare(host="0.0.0.0", port=8080)
    Sanic.serve(primary=app, app_loader=loader)
