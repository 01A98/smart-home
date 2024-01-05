from sanic import Request, Sanic
from sanic.views import HTTPMethodView
from sanic_ext import render
from tortoise.transactions import atomic

from .. import NAVIGATION, Page, PageContext
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
            rooms = await Room.all().prefetch_related("bulbs")
            return await render(
                self.page.template_path,
                context={
                    "rooms": rooms,
                    **PageContext(current_page=self.page).model_dump(),
                },
            )

    app.add_route(RoomsView.as_view(), "/rooms")

    NAVIGATION["rooms"] = RoomsView.page
