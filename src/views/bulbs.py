import asyncio
from sanic import Request, Sanic, json
from sanic.views import HTTPMethodView
from tortoise.transactions import atomic

from ..wiz import send_message_to_wiz

from ..models import Bulb, Bulb_Py
from . import NAVIGATION, Page, PageContext


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
            bulbs = [
                (await Bulb_Py.from_tortoise_orm(bulb)).model_dump()
                for bulb in await Bulb.all()
            ]
            return {"bulbs": bulbs, **PageContext(current_page=self.page).model_dump()}

    async def get_all_bulbs_info(request: Request):
        bulbs = await Bulb.all()
        ip_addresses = [bulb.ip for bulb in bulbs]

        bulbs_info = await asyncio.gather(
            *[send_message_to_wiz(ip) for ip in ip_addresses]
        )
        return json(bulbs_info)

    app.add_route(BulbsView.as_view(), BulbsView.page.path, name=BulbsView.page.name)
    app.add_route(
        get_all_bulbs_info, f"{BulbsView.page.path}/info/all", name="bulbs_info_all"
    )
    NAVIGATION["bulbs"] = BulbsView.page
