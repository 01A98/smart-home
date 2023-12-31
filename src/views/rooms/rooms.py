import asyncio
from sanic import Request, Sanic
from sanic_ext.extensions.templating.render import TemplateResponse
from sanic.views import HTTPMethodView
from tortoise.transactions import atomic

from ...wiz import send_message_to_wiz

from ...models import Bulb, Room
from .. import NAVIGATION, Page, PageContext


def create_view(app: Sanic) -> None:
    class RoomsView(HTTPMethodView):
        decorators = [atomic()]
        page = Page(
            name="rooms",
            path="/rooms",
            title="Pokoje",
            template_path="views/rooms/get.html",
        )

        @app.ext.template(page.template_path)
        async def get(self, request: Request):
            rooms = await Room.all().values("id", "name")
            return {"rooms": rooms, **PageContext(current_page=self.page).model_dump()}

    @app.ext.template("views/rooms/card-grid.html")
    async def get_rooms_with_bulb_info(request: Request):
        rooms = await Room.all().values("id", "name")
        room_ids = [room["id"] for room in rooms]

        bulbs = await Bulb.filter(room_id__in=room_ids).only(
            "id", "ip", "name", "room_id"
        )
        await asyncio.gather(*[bulb.assign_wiz_info() for bulb in bulbs])

        for room in rooms:
            room["bulbs"] = [bulb for bulb in bulbs if bulb["room_id"] == room["id"]]

        return {"rooms": rooms}

    app.add_route(RoomsView.as_view(), RoomsView.page.path, name=RoomsView.page.name)
    app.add_route(
        get_rooms_with_bulb_info,  # type: ignore
        f"{RoomsView.page.path}/bulb-info/all",
        name="rooms_with_bulb_info",
    )
    NAVIGATION["rooms"] = RoomsView.page
