from sanic import Request, Sanic
from sanic.views import HTTPMethodView
from sanic_ext import render
from tortoise.transactions import atomic

from .. import NAVIGATION, Page, BaseContext
from ...components.base_page import base_page
from ...components.breadcrumbs import breadcrumbs
from ...components.navbar import navbar
from ...components.room_temperature_button_group import room_temperature_button_group
from ...components.spinner import spinner
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
            rooms_py = await Room.get_all()

            base_ctx = BaseContext(app=app, current_page=self.page)
            base = base_page(
                navbar(app, base_ctx.navigation, self.page),
                breadcrumbs(app, base_ctx.navigation["home"], self.page),
                spinner(htmx_indicator=True),
                title=self.page.title,
            )

            # return html(
            #     str(base),
            #     headers={"X-Rooms": json.dumps(rooms_py, default=pydantic_encoder)},
            # )

            return await render(
                self.page.template_path,
                context={
                    "rooms": rooms,
                    "spinner": str(spinner(htmx_indicator=True)),
                    "room_temperature_button_groups": {
                        room.id: str(room_temperature_button_group(room, app))
                        for room in rooms
                    },
                    **BaseContext(app=app, current_page=self.page).model_dump(),
                },
            )

    app.add_route(RoomsView.as_view(), "/rooms")

    NAVIGATION["rooms"] = RoomsView.page
