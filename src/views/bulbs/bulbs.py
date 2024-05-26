from itertools import groupby

from sanic import Request, Sanic, html
from sanic.views import HTTPMethodView
from sanic_ext import serializer
from tortoise.transactions import atomic
from dominate.tags import div, section, a, h2, p, small

from src.components.spinner import Spinner
from src.models.bulb import Bulb
from src.views import NAVIGATION, Page, BaseContext
from src.components.base_page import BasePage
from src.components.breadcrumbs import Breadcrumbs
from src.components.new_item_button import NewItemButton
from src.components.nothing_here import NothingHere
from src.components.bulb_icon import BulbIcon


def create_view(app: Sanic) -> None:
    class BulbsView(HTTPMethodView):
        decorators = [atomic(), serializer(html)]
        page = Page(
            name="BulbsView",
            title="Żarówki",
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

            base_ctx = BaseContext(app=app, current_page=self.page)
            navbar = base_ctx.app_navbar

            page_content = BasePage(
                navbar,
                div(
                    Breadcrumbs(app, base_ctx.navigation["home"], self.page),
                    class_name="w-full max-w-screen-xl mx-auto p-2",
                ),
                section(
                    div(
                        NewItemButton(href=app.url_for("BulbView", id="new")),
                        class_name="block mx-auto w-full max-w-screen-xl pt-6 py-6 px-2",
                    ),
                    div(
                        *[
                            self._room_section(room_name, bulbs, app)
                            for room_name, bulbs in bulbs_by_room_name.items()
                        ]
                        or [NothingHere()],
                        class_name="w-full h-full max-w-screen-xl py-6 px-4 mx-auto mx-4",
                    ),
                ),
                title=self.page.title,
            )

            return page_content.render()

        @staticmethod
        def _room_section(room_name, bulbs, app):
            with div(
                class_name="my-6 flex flex-col border border-gray-300 dark:border-gray-700 rounded-md p-8"
            ):
                a(
                    h2(
                        room_name,
                        class_name="text-2xl font-bold text-gray-800 dark:text-gray-100",
                    ),
                    href=app.url_for("RoomView", id=bulbs[0].room_id)
                    if bulbs[0].room
                    else "#",
                    class_name="self-end",
                )
                room_bulbs = [BulbsView._bulb_card(bulb, app) for bulb in bulbs]
                return room_bulbs

        @staticmethod
        def _bulb_card(bulb, app):
            with div(
                class_name="my-8 min-w-fit rounded-md text-white bg-indigo-700 hover:bg-pink-700 flex flex-col shadow-gray-200 dark:shadow-gray-900 duration-300 hover:-translate-y-1"
            ) as card:
                with div(class_name="p-4 self-start"):
                    a(
                        bulb.name,
                        class_name="text-lg hover:-translate-y-[2px] mb-4 font-semibold leading-relaxed text-gray-200 dark:text-white",
                        href=app.url_for("BulbView", id=bulb.id),
                    )
                with div(id=f"bulb-info-{bulb.id}", class_name="px-2 mb-4"):
                    div(
                        **{
                            "hx-get": app.url_for("bulb_with_state", id=bulb.id),
                            "hx-trigger": "load",
                            "hx-swap": "innerHTML",
                            "hx-indicator": "app-spinner",
                            "hx-target": f"#bulb-info-{bulb.id}",
                        }
                    )
                    Spinner(htmx_indicator=True)
            return card

    app.add_route(BulbsView.as_view(), "/bulbs")
    NAVIGATION["bulbs"] = BulbsView.page
