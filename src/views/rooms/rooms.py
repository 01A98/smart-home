from dataclasses import dataclass
from typing import Set, Any, Callable, Coroutine, Literal, Optional
import os
import asyncio
from dominate.tags import (
    button,
    div,
    form,
    html_tag,
    label,
    option,
    p,
    section,
    select,
    small,
    span,
)
from sanic import HTTPResponse, Request, Sanic, json
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
from src.control import set_scene_id, set_temperature_by_name
from src.components.material_icons import Icon
from src.models.bulb import Bulb
from src.models.room import Room
from src.views import NAVIGATION, ROUTES, BaseContext, Page
from src.wiz import send_message_to_wiz, MESSAGES
from src.utils import run_command
import asyncio


@dataclass
class Routes:
    TURN_BULB_ON: str = "turn_bulb_on"
    TURN_BULB_OFF: str = "turn_bulb_off"
    SELECT_SCENE_ID: str = "set_scene_id"
    SELECT_TEMPERATURE: str = "set_temperature_by_name"
    TURN_ALL_OFF: str = "turn_all_off"


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
                # name="Gabinet",
            ).prefetch_related("bulbs")

            base_ctx = BaseContext(app=app, current_page=self.page)
            navbar = base_ctx.app_navbar
            scenes = base_ctx.settings.scenes
            temperature_settings = base_ctx.settings.temperature_settings

            page_content = BasePage(
                navbar,
                div(
                    Breadcrumbs(app, base_ctx.navigation["home"], self.page),
                    class_name="w-full max-w-screen-xl mx-auto p-2",
                ),
                section(
                    div(
                        NewItemButton(href=app.url_for("RoomView", id="new")),
                        button(
                            Icon("power_off", class_name="material-symbols-rounded"),
                            class_name="text-black bg-gray-100 hover:bg-gray-200 focus:outline-none "
                            "focus:ring-4 focus:ring-pink-600 font-medium max-w-screen-xl rounded-md text-md px-4 py-3 "
                            "text-center mr-6",
                            **{
                                "hx-post": app.url_for(ROUTES["turn_all_off"]),
                                "hx-swap": "none",
                            },
                        ),
                        class_name="flex flex-row justify-between items-end w-full mx-auto h-full pt-6 py-6 px-2",
                    ),
                    div(
                        room_card_grid(rooms, app, scenes, temperature_settings),
                        class_name="w-full h-full max-w-screen-xl pb-6 px-4 mx-auto mx-4",
                    ),
                    class_name="block w-full max-w-screen-xl mx-auto",
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

    async def turn_all_off(request: Request):
        bulbs = await Bulb.all()

        await asyncio.gather(
            *[send_message_to_wiz(bulb.ip, MESSAGES["OFF"]) for bulb in bulbs]
        )

        res = html("ok")
        res.headers.add("HX-Trigger", "turn-all-off")
        return res

    async def _set_scene_id(request: Request, id: int):
        scene_id: int = request.form.get("scene_id")
        if not scene_id:
            return html("No scene_id provided", 400)

        res = html("ok", 200)

        if scene_id == 0:
            return res

        # TODO: parse included bulbs in some function, add validation
        included_bulb_suffix = "include-bulb-"
        bulb_ids = [
            int(key.replace(included_bulb_suffix, ""))
            for key in request.form.keys()
            if included_bulb_suffix in key
        ]
        await set_scene_id(bulb_ids, scene_id)

        if len(bulb_ids) > 0:
            hx_trigger = "change-room-state"
            res.headers.add("HX-Trigger", hx_trigger)

        return res

    async def _set_temperature_by_name(request: Request, id: int):
        temperature: Optional[
            Literal["warmest", "warmer", "warm", "cold", "colder", "coldest"]
        ] = request.form.get("temperature")

        if not temperature:
            return html("No temperature setting name provided", 400)

        # TODO: parse included bulbs in some function, add validation
        included_bulb_suffix = "include-bulb-"
        bulb_ids = [
            int(key.replace(included_bulb_suffix, ""))
            for key in request.form.keys()
            if included_bulb_suffix in key
        ]
        await set_temperature_by_name(bulb_ids, temperature)

        res = html("ok", 200)
        if len(bulb_ids) > 0:
            hx_trigger = "change-room-state"
            res.headers.add("HX-Trigger", hx_trigger)

        return res

    async def get_devices_on_network(request: Request):
        bulbs = await Bulb.all()
        bulb_with_ips = [(bulb.ip, bulb.name) for bulb in bulbs]

        arp_scan = await run_command("arp-scan", "-l")
        lines = [line.split("\t") for line in arp_scan.split("\n")]

        filtered = list(filter(lambda line: line[0][:3] == "192", lines))
        ip_addresses = [(ip, name) for ip, _mac, name in filtered]
        res = {
            "found_on_network": ip_addresses,
            "bulbs": bulb_with_ips,
            "found_but_not_in_bulbs": [
                (ip, name)
                for ip, name in ip_addresses
                if ip not in [ip for ip, _name in bulb_with_ips]
            ],
        }
        return json(res)

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
    app.add_route(
        _set_scene_id,
        "rooms/<id:int>/scene_id",
        methods=["POST"],
        name=Routes.SELECT_SCENE_ID,
    )
    app.add_route(
        _set_temperature_by_name,
        "rooms/<id:int>/temperature",
        methods=["POST"],
        name=Routes.SELECT_TEMPERATURE,
    )
    # TODO: move to own file?
    app.add_route(
        turn_all_off, "turn_all_off", methods=["POST"], name=Routes.TURN_ALL_OFF
    )
    app.add_route(
        get_devices_on_network,
        "network_devices",
        methods=["GET"],
        name="network_devices",
    )

    NAVIGATION["rooms"] = RoomsView.page
    ROUTES[BulbIcon.route] = BulbIcon.route
    ROUTES[Routes.TURN_BULB_ON] = Routes.TURN_BULB_ON
    ROUTES[Routes.TURN_BULB_OFF] = Routes.TURN_BULB_OFF
    ROUTES[Routes.SELECT_SCENE_ID] = Routes.SELECT_SCENE_ID
    ROUTES[Routes.SELECT_TEMPERATURE] = Routes.SELECT_TEMPERATURE
    ROUTES[Routes.TURN_ALL_OFF] = Routes.TURN_ALL_OFF


def room_card_grid(
    rooms: list[Room],
    app: Sanic,
    scenes: list[tuple[str, str]],
    temperature_settings: list[tuple[str, str]],
) -> html_tag:
    with div(
        class_name="grid grid-flow-row gap-8 sm:grid-cols-2 md:grid-cols-3 "
        "lg:grid-cols-4"
    ) as div_:
        if len(rooms) == 0:
            NothingHere()
        else:
            for room in rooms:
                room_card(room, app, scenes, temperature_settings)
    return div_


def room_card(
    room: Room,
    app: Sanic,
    scenes: list[tuple[str, str]],
    temperature_settings: list[tuple[str, str]],
) -> html_tag:
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
                    # Select scene id
                    with div(class_name="relative h-10 w-full"):
                        with select(
                            class_name="peer h-full w-full rounded-[7px] border border-blue-gray-200 "
                            "border-t-transparent bg-transparent px-3 py-2.5 font-sans text-sm "
                            "font-normal text-blue-gray-700 outline outline-0 transition-all "
                            "placeholder-shown:border placeholder-shown:border-blue-gray-200 "
                            "placeholder-shown:border-t-blue-gray-200 empty:!bg-gray-900 "
                            "focus:border-2 focus:border-gray-900 focus:border-t-transparent "
                            "focus:outline-0 disabled:border-0 disabled:bg-blue-gray-50",
                            name="scene_id",
                            **{
                                "hx-post": app.url_for(
                                    Routes.SELECT_SCENE_ID, id=room.id
                                ),
                                "hx-swap": "none",
                                "hx-include": "closest form",
                            },
                        ):
                            option("Nie wybrano trybu", value="0")
                            for scene in scenes:
                                option(scene[1], value=scene[0])
                        label(
                            "Wybierz tryb",
                            class_name="before:content[' '] after:content[' '] pointer-events-none absolute left-0 -top-1.5 flex h-full w-full select-none text-[11px] font-normal leading-tight text-blue-gray-400 transition-all before:pointer-events-none before:mt-[6.5px] before:mr-1 before:box-border before:block before:h-1.5 before:w-2.5 before:rounded-tl-md before:border-t before:border-l before:border-blue-gray-200 before:transition-all after:pointer-events-none after:mt-[6.5px] after:ml-1 after:box-border after:block after:h-1.5 after:w-2.5 after:flex-grow after:rounded-tr-md after:border-t after:border-r after:border-blue-gray-200 after:transition-all peer-placeholder-shown:text-sm peer-placeholder-shown:leading-[3.75] peer-placeholder-shown:text-blue-gray-500 peer-placeholder-shown:before:border-transparent peer-placeholder-shown:after:border-transparent peer-focus:text-[11px] peer-focus:leading-tight peer-focus:text-gray-900 peer-focus:before:border-t-2 peer-focus:before:border-l-2 peer-focus:before:border-gray-900 peer-focus:after:border-t-2 peer-focus:after:border-r-2 peer-focus:after:border-gray-900 peer-disabled:text-transparent peer-disabled:before:border-transparent peer-disabled:after:border-transparent peer-disabled:peer-placeholder-shown:text-blue-gray-500",
                        )
                    # Select temperature
                    # TODO: move to component
                    with div(class_name="relative h-10 w-full"):
                        with select(
                            class_name="peer h-full w-full rounded-[7px] border border-blue-gray-200 "
                            "border-t-transparent bg-transparent px-3 py-2.5 font-sans text-sm "
                            "font-normal text-blue-gray-700 outline outline-0 transition-all "
                            "placeholder-shown:border placeholder-shown:border-blue-gray-200 "
                            "placeholder-shown:border-t-blue-gray-200 empty:!bg-gray-900 "
                            "focus:border-2 focus:border-gray-900 focus:border-t-transparent "
                            "focus:outline-0 disabled:border-0 disabled:bg-blue-gray-50",
                            name="temperature",
                            **{
                                "hx-post": app.url_for(
                                    Routes.SELECT_TEMPERATURE, id=room.id
                                ),
                                "hx-swap": "none",
                                "hx-include": "closest form",
                            },
                        ):
                            option("Nie wybrano temperatury", value="warm")
                            for temperature_setting in temperature_settings:
                                option(
                                    temperature_setting[1], value=temperature_setting[0]
                                )
                        label(
                            "Wybierz temperaturę koloru",
                            class_name="before:content[' '] after:content[' '] pointer-events-none absolute left-0 -top-1.5 flex h-full w-full select-none text-[11px] font-normal leading-tight text-blue-gray-400 transition-all before:pointer-events-none before:mt-[6.5px] before:mr-1 before:box-border before:block before:h-1.5 before:w-2.5 before:rounded-tl-md before:border-t before:border-l before:border-blue-gray-200 before:transition-all after:pointer-events-none after:mt-[6.5px] after:ml-1 after:box-border after:block after:h-1.5 after:w-2.5 after:flex-grow after:rounded-tr-md after:border-t after:border-r after:border-blue-gray-200 after:transition-all peer-placeholder-shown:text-sm peer-placeholder-shown:leading-[3.75] peer-placeholder-shown:text-blue-gray-500 peer-placeholder-shown:before:border-transparent peer-placeholder-shown:after:border-transparent peer-focus:text-[11px] peer-focus:leading-tight peer-focus:text-gray-900 peer-focus:before:border-t-2 peer-focus:before:border-l-2 peer-focus:before:border-gray-900 peer-focus:after:border-t-2 peer-focus:after:border-r-2 peer-focus:after:border-gray-900 peer-disabled:text-transparent peer-disabled:before:border-transparent peer-disabled:after:border-transparent peer-disabled:peer-placeholder-shown:text-blue-gray-500",
                        )

    return div_
