from itertools import groupby

from sanic import Request, Sanic
from sanic.views import HTTPMethodView
from sanic_ext import render
from tortoise.transactions import atomic

from src.components.spinner import Spinner
from src.models.bulb import Bulb
from src.views import NAVIGATION, Page, BaseContext


def create_view(app: Sanic) -> None:
    class BulbsView(HTTPMethodView):
        decorators = [atomic()]
        page = Page(
            name="BulbsView",
            title="Żarówki",
            template_path="views/bulbs/get.html",
        )

        async def get(self, request: Request):
            bulbs = await Bulb.all().prefetch_related("room")

            bulbs_by_room_name_grouped = groupby(
                bulbs,
                lambda bulb: bulb.room.name if bulb.room else "Bez przypisanego pokoju",
            )
            bulbs_by_room_name = {
                room_name: list(bulbs)
                for room_name, bulbs in bulbs_by_room_name_grouped
            }

            return await render(
                self.page.template_path,
                context={
                    "bulbs_by_room_name": bulbs_by_room_name,
                    "spinner": str(Spinner(htmx_indicator=True)),
                    **BaseContext(app=app, current_page=self.page).model_dump(),
                },
            )

    app.add_route(BulbsView.as_view(), "/bulbs")
    NAVIGATION["bulbs"] = BulbsView.page
