from typing import Any, Callable

from sanic import Sanic
from sanic.response import redirect
from sanic.worker.loader import AppLoader
from tortoise.contrib.sanic import register_tortoise

import src.logger  # noqa
from src.settings import SETTINGS
from src.views import create_views


def attach_endpoints(app: Sanic):
    create_views(app)


def serve_static_files(app: Sanic):
    app.static("/public", "./public", name="public", directory_view=True)
    app.static("/assets", "./assets", name="assets", directory_view=True)


def apply_static_redirects(app: Sanic):
    # https://sanic.dev/en/guide/how-to/static-redirects.html#static-redirects
    def get_static_function(value: Any) -> Callable[..., Any]:
        return lambda *_, **__: value

    for src_, dest in SETTINGS.static_redirects.items():
        response = redirect(dest)
        handler = get_static_function(response)
        app.route(src_)(handler)


def create_app() -> Sanic:
    app = Sanic("smart-home")
    app.config.TEMPLATING_ENABLE_ASYNC = True

    attach_endpoints(app)
    serve_static_files(app)
    apply_static_redirects(app)

    register_tortoise(
        app,
        db_url=str(SETTINGS.db_url),
        modules={
            "models": [
                "src.models.bulb",
                "src.models.room",
                "src.models.icon",
                "src.models.setting",
            ]
        },
        generate_schemas=True,
    )

    return app


if __name__ == "__main__":
    loader = AppLoader(factory=create_app)
    app = loader.load()
    app.prepare(host="0.0.0.0", port=8080)
    Sanic.serve(primary=app, app_loader=loader)
