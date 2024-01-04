import asyncio

from sanic import Request, Sanic
from sanic.views import HTTPMethodView
from sanic_ext import render
from tortoise.transactions import atomic

from .. import NAVIGATION, Page, PageContext
from ...models.bulb import Bulb
from ...models.room import Room


def create_view(app: Sanic) -> None:
    class RoomsView(HTTPMethodView):
        decorators = [atomic()]
        page = Page(
            name="RoomsView",
            title="Pokoje",
            template_path="views/rooms/get.html",
        )

        async def get(self, request: Request):
            rooms = await Room.all().values("id", "name")
            return await render(
                self.page.template_path,
                context={
                    "rooms": rooms,
                    **PageContext(current_page=self.page).model_dump(),
                },
            )

    async def get_rooms_with_bulb_info(request: Request):
        rooms = await Room.all().values("id", "name")
        room_ids = [room["id"] for room in rooms]

        bulbs = await Bulb.filter(room_id__in=room_ids).all()
        await asyncio.gather(*[bulb.assign_wiz_info() for bulb in bulbs])

        for room in rooms:
            room["bulbs"] = [bulb for bulb in bulbs if bulb["room_id"] == room["id"]]

        return await render("views/rooms/card-grid.html", context={"rooms": rooms})

    app.add_route(RoomsView.as_view(), "/rooms")
    app.add_route(
        get_rooms_with_bulb_info,
        "rooms/bulb-info/all",
        name="rooms_with_bulb_info",
    )
    NAVIGATION["rooms"] = RoomsView.page
