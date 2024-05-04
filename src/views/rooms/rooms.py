from dataclasses import dataclass
from typing import Callable, Coroutine, Any

from dominate.tags import (
    div,
    section,
    p,
    html_tag,
    small,
    form,
    span,
    button,
    select,
    option,
    label,
)
from sanic import Request, Sanic, HTTPResponse
from sanic.response import html
from sanic.views import HTTPMethodView
from sanic_ext import serializer
from tortoise.transactions import atomic

from src.components.base_page import BasePage
from src.components.breadcrumbs import Breadcrumbs
from src.components.bulb_icon import BulbIcon
from src.components.checkbox import Checkbox
from src.components.new_item_button import NewItemButton
from src.components.nothing_here import NothingHere
from src.components.room_brightness_slider import RoomBrightnessSlider
from src.components.room_light_switch import RoomLightSwitch
from src.models.bulb import Bulb
from src.models.room import Room
from src.views import NAVIGATION, Page, BaseContext, ROUTES


@dataclass
class Routes:
    TURN_BULB_ON: str = "turn_bulb_on"
    TURN_BULB_OFF: str = "turn_bulb_off"


@dataclass
class Selectors:
    INCLUDE_BULB_CHECKBOX: str = '[name="include-bulb-checkbox"]'


def create_view(app: Sanic) -> None:
    class RoomsView(HTTPMethodView):
        decorators = [atomic(), serializer(html)]
        page = Page(
            name="RoomsView",
            title="Pokoje",
        )

        async def get(self, request: Request):
            rooms = await Room.filter(
                name="Gabinet",
            ).prefetch_related("bulbs")

            base_ctx = BaseContext(app=app, current_page=self.page)
            navbar = base_ctx.app_navbar
            scenes = base_ctx.settings.scenes

            page_content = BasePage(
                navbar,
                div(
                    Breadcrumbs(app, base_ctx.navigation["home"], self.page),
                    class_name="w-full max-w-screen-xl mx-auto p-2",
                ),
                section(
                    div(
                        NewItemButton(href=app.url_for("RoomView", id="new")),
                        class_name="block mx-auto w-full max-w-screen-xl py-6 px-2",
                    ),
                    room_card_grid(rooms, app, scenes),
                    class_name="w-full h-full max-w-screen-xl py-6 px-4 mx-auto mx-4",
                ),
                title=self.page.title,
            )

            return page_content.render()

    @serializer(html)
    async def get_bulb_with_state(request: Request, id: int):
        bulb = await Bulb.get(id=id)
        await bulb.assign_wiz_info()
        return BulbIcon(app, bulb).render()

    def change_bulb_state_handler(
        state: bool,
    ) -> Callable[[Request, int], Coroutine[Any, Any, HTTPResponse]]:
        hx_trigger = "change-bulb-state"

        async def handler(request: Request, id: int):
            bulb = await Bulb.get(id=id)
            await bulb.toggle_state(state)
            content = BulbIcon(app, bulb)

            res = html(content.render())
            res.headers.add("HX-Trigger", hx_trigger)

            return res

        return handler

    app.add_route(RoomsView.as_view(), "/rooms")
    app.add_route(
        get_bulb_with_state,
        "bulbs/<id:int>/state",
        name=BulbIcon.route,
    )
    app.add_route(
        change_bulb_state_handler(True), "bulbs/<id:int>/on", name=Routes.TURN_BULB_ON
    )
    app.add_route(
        change_bulb_state_handler(False),
        "bulbs/<id:int>/off",
        name=Routes.TURN_BULB_OFF,
    )

    NAVIGATION["rooms"] = RoomsView.page
    ROUTES[BulbIcon.route] = BulbIcon.route
    ROUTES[Routes.TURN_BULB_ON] = Routes.TURN_BULB_ON
    ROUTES[Routes.TURN_BULB_OFF] = Routes.TURN_BULB_OFF


def room_card_grid(
    rooms: list[Room], app: Sanic, scenes: list[tuple[str, str]]
) -> html_tag:
    with div(
        class_name="grid grid-flow-row gap-8 sm:grid-cols-2 md:grid-cols-3 "
        "lg:grid-cols-4"
    ) as div_:
        if len(rooms) == 0:
            NothingHere()
        else:
            for room in rooms:
                room_card(room, app, scenes)
    return div_


def room_card(room: Room, app: Sanic, scenes: list[tuple[str, str]]) -> html_tag:
    with form(
        id=f"room-{room.id}",
        event_container=True,
        class_name="w-full flex flex-col rounded-xl bg-white border-2 border-gray-100 text-gray-700 shadow-lg",
        **{
            "x-data": """{
                    checked: false,
                    checkboxes: [],
                    init() {
                        this.checkboxes = Array.from(this.$el.querySelectorAll("[checkbox]"))
                        const allChecked = this.checkboxes.every(box => box.checked === true)
                        if (allChecked) {
                            this.checked = true
                        }
                        window.addEventListener('input-checked', (_event) => {
                            const allUnchecked = this.checkboxes.every(box => box.checked === false)
                            if (allUnchecked) {
                                this.checked = false
                            } else {
                                this.checked = true
                            }
                        })
                    },
                    toggle() {
                        this.checked = !this.checked
                        for (const checkbox of this.checkboxes) {
                            checkbox.checked = this.checked
                        }
                    }
                }""",
        },
    ) as div_:
        # Name and description
        with div(class_name="p-4 w-full flex flex-row justify-between"):
            p(room.name, class_name="text-lg font-semibold leading-relaxed")
            if room.description:
                small(room.description, class_name="leading-5 text-gray-500 mt-2")
                # Check bulbs to include when controlling
            with button(
                type="button",
                class_name="self-end w-fit py-2 px-3 rounded-full",
                **{
                    "data-ripple-light": "true",
                    "data-ripple-dark": "true",
                    "@click": "toggle",
                },
            ) as button_:
                span(
                    class_name="material-icons-round",
                    **{"x-text": "checked ? 'remove_done': 'done_all'"},
                )

        # Bulbs
        with div(class_name="flex flex-col items-end gap-1 px-6 h-min"):
            for bulb in room.bulbs:
                with div(class_name="flex flex-row w-full gap-3"):
                    BulbIcon.lazy_load(app, bulb)
                    Checkbox(
                        name=f"include-bulb-{bulb.id}",
                        id_=f"include-bulb-{bulb.id}",
                        event=("change", "$dispatch('input-checked', this.checked)"),
                    )

        # Group controls
        with div(
            class_name=f"w-full flex flex-col my-8 px-8 {'border-t pt-4' if room.bulbs else ''} border-gray-500"
        ):
            if room.bulbs:
                with div(
                    class_name="w-full flex flex-col justify-center items-end gap-y-4"
                ):
                    RoomBrightnessSlider.lazy_load(app, room)
                    RoomLightSwitch.lazy_load(app, room)
                    # TODO: move to component
                    with div(class_name="relative h-10 w-full"):
                        with select(
                            class_name="peer h-full w-full rounded-[7px] border border-blue-gray-200 "
                            "border-t-transparent bg-transparent px-3 py-2.5 font-sans text-sm "
                            "font-normal text-blue-gray-700 outline outline-0 transition-all "
                            "placeholder-shown:border placeholder-shown:border-blue-gray-200 "
                            "placeholder-shown:border-t-blue-gray-200 empty:!bg-gray-900 "
                            "focus:border-2 focus:border-gray-900 focus:border-t-transparent "
                            "focus:outline-0 disabled:border-0 disabled:bg-blue-gray-50"
                        ):
                            option("Wybierz któryś tryb z listy", value="")
                            for scene in scenes:
                                option(scene[1], value=scene[0])
                        label(
                            "Wybierz tryb",
                            class_name="before:content[' '] after:content[' '] pointer-events-none absolute left-0 -top-1.5 flex h-full w-full select-none text-[11px] font-normal leading-tight text-blue-gray-400 transition-all before:pointer-events-none before:mt-[6.5px] before:mr-1 before:box-border before:block before:h-1.5 before:w-2.5 before:rounded-tl-md before:border-t before:border-l before:border-blue-gray-200 before:transition-all after:pointer-events-none after:mt-[6.5px] after:ml-1 after:box-border after:block after:h-1.5 after:w-2.5 after:flex-grow after:rounded-tr-md after:border-t after:border-r after:border-blue-gray-200 after:transition-all peer-placeholder-shown:text-sm peer-placeholder-shown:leading-[3.75] peer-placeholder-shown:text-blue-gray-500 peer-placeholder-shown:before:border-transparent peer-placeholder-shown:after:border-transparent peer-focus:text-[11px] peer-focus:leading-tight peer-focus:text-gray-900 peer-focus:before:border-t-2 peer-focus:before:border-l-2 peer-focus:before:border-gray-900 peer-focus:after:border-t-2 peer-focus:after:border-r-2 peer-focus:after:border-gray-900 peer-disabled:text-transparent peer-disabled:before:border-transparent peer-disabled:after:border-transparent peer-disabled:peer-placeholder-shown:text-blue-gray-500",
                        )
    return div_
