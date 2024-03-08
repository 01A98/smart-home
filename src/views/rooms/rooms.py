from dominate.tags import div, section, p, a, h3, html_tag, small
from sanic import Request, Sanic, html
from sanic.views import HTTPMethodView
from tortoise.transactions import atomic

from components.base_page import BasePage
from components.breadcrumbs import Breadcrumbs
from components.material_icons import Icon
from components.new_item_button import NewItemButton
from components.nothing_here import NothingHere
from components.spinner import Spinner
from models.room import Room
from views import NAVIGATION, Page, BaseContext


def create_view(app: Sanic) -> None:
    class RoomsView(HTTPMethodView):
        decorators = [atomic()]
        page = Page(
            name="RoomsView",
            title="Pokoje",
        )

        async def get(self, request: Request):
            rooms = await Room.all().prefetch_related("bulbs")

            base_ctx = BaseContext(app=app, current_page=self.page)
            navbar = base_ctx.app_navbar

            page_content = BasePage(
                navbar,
                div(
                    Breadcrumbs(app, base_ctx.navigation["home"], self.page),
                    class_name="w-full max-w-screen-xl mx-auto p-2"
                ),
                section(
                    div(
                        NewItemButton(href=app.url_for('RoomView', id='new')),
                        class_name="block mx-auto w-full max-w-screen-xl py-6 px-2"
                    ),
                    room_card_grid(rooms, app),
                    class_name="w-full h-full max-w-screen-xl py-6 px-2 mx-auto"
                ),
                title=self.page.title,
            )

            return html(page_content.render())

    app.add_route(RoomsView.as_view(), "/rooms")

    NAVIGATION["rooms"] = RoomsView.page


def room_card_grid(rooms: list[Room], app: Sanic) -> html_tag:
    with div(
            class_name="grid grid-flow-row p-4 gap-8 sm:grid-cols-2 md:grid-cols-3 "
                       "lg:grid-cols-4 xl:grid-cols-5"
    ) as div_:
        if len(rooms) == 0:
            NothingHere()
        else:
            for room in rooms:
                room_card(room, app)
    return div_


def room_card(room: Room, app: Sanic) -> html_tag:
    with div(
            id=f"card-item-{room.id}",
            class_name="flex w-full flex-col rounded-xl bg-white bg-clip-border text-gray-700 shadow-lg"
    ) as div_:
        # Name and description
        with div(class_name="p-4 self-start"):
            p(
                room.name,
                class_name="text-lg font-semibold leading-relaxed"
            )
            if room.description:
                small(
                    room.description,
                    class_name="leading-5 text-gray-500 mt-2"
                )
        # Bulbs
        with div(
                class_name="flex flex-col gap-1 px-2"
        ):
            for bulb in room.bulbs:
                with div(id=f"bulb-info-{bulb.id}"):
                    # div(**{
                    #     "hx-get": app.url_for('bulb_with_wiz_info', id=bulb.id, with_name=True),
                    #     "hx-trigger": "load",
                    #     "hx-swap": "innerHTML",
                    #     "hx-indicator": "app-spinner",
                    #     "hx-target": f"#bulb-info-{bulb.id}"
                    # })
                    Spinner(htmx_indicator=True)
        # Group controls
        with div(

                class_name=f"flex flex-row justify-between my-8 px-4 items-center "
                           f"{'border-t pt-4' if room.bulbs else ''} border-gray-500"
        ):
            if room.bulbs:
                bulbs_state_container_id = f"room-{room.id}-bulbs-state"

                with div(class_name="flex flex-col justify-center items-start gap-y-3"):
                    h3("Steruj wszystkimi", class_name="font-bold")

                    with div(id=bulbs_state_container_id, class_name="ml-2"):
                        div(**{
                            "hx-get": app.url_for('room_bulbs_state', id=room.id),
                            "hx-trigger": "load",
                            "hx-swap": "innerHTML",
                            "hx-indicator": "app-spinner",
                            "hx-target": f"#{bulbs_state_container_id}"
                        })
                        Spinner(htmx_indicator=True)

                    with div(class_name="flex flex-row gap-x-1"):
                        with div(id=f"room-{room.id}-bulbs-brightness", class_name="ml-2"):
                            div(**{
                                "hx-get": app.url_for('room_bulbs_brightness', id=room.id),
                                "hx-trigger": "load",
                                "hx-swap": "innerHTML",
                                "hx-indicator": "app-spinner",
                                "hx-target": f"#room-{room.id}-bulbs-brightness"
                            })
                            Spinner(htmx_indicator=True)

            with a(
                    href=app.url_for("RoomView", id=room.id),
                    class_name="cursor-pointer self-end py-1 px-2 bg-gray-200 rounded-md flex flex-col items-center",
                    data_ripple_light="true",
                    data_ripple_dark="true"
            ):
                Icon("mode_edit")
                p("Edytuj pokój", class_name="text-xs")
    return div_
