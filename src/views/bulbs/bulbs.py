import asyncio
from markupsafe import Markup
from sanic import Request, Sanic, json
from sanic.views import HTTPMethodView
from sanic.response import html
from tortoise.transactions import atomic

from ...wiz import send_message_to_wiz

from ...models import Bulb, Bulb_Py
from .. import NAVIGATION, Page, PageContext


def create_view(app: Sanic) -> None:
    class BulbsView(HTTPMethodView):
        decorators = [atomic()]
        page = Page(
            name="bulbs",
            path="/bulbs",
            title="Żarówki",
            template_path="views/bulbs/get.html",
        )

        @app.ext.template(page.template_path)
        async def get(self, request: Request):
            bulbs = await Bulb.all()
            return {"bulbs": bulbs, **PageContext(current_page=self.page).model_dump()}

    app.add_route(BulbsView.as_view(), BulbsView.page.path, name=BulbsView.page.name)
    NAVIGATION["bulbs"] = BulbsView.page
