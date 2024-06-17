from dominate.tags import section, div
from sanic import Request, Sanic, html, redirect
from sanic.views import HTTPMethodView
from sanic_ext import serializer
from tortoise.transactions import atomic

from src.components.base_page import BasePage
from src.components.breadcrumbs import Breadcrumbs
from src.components.room_brightness_slider import RoomBrightnessSlider
from src.components.room_light_switch import RoomLightSwitch
from src.models.room import Room, RoomForm
from src.control import change_brightness, toggle_state
from src.views import Page, BaseContext


def get_room_state_from_form(form: RoomForm) -> bool:
    previous_state = form.get("room_state_value")
    updated_state = form.get("room_state", default=None)
    # TODO: this might be a bug
    bulb_state = None

    if previous_state == "false" and updated_state == "on":
        bulb_state = True
    if previous_state == "true" and updated_state is not None:
        bulb_state = False
    return bulb_state


def create_view(app: Sanic) -> None:
    class RoomView(HTTPMethodView):
        decorators = [atomic()]

        @staticmethod
        async def post(request: Request):
            form = RoomForm(request.form)
            await Room.create(**form.data)
            return redirect(app.url_for("RoomsView"))

        @staticmethod
        async def delete(request: Request):
            room_id = request.args.get("id")
            await Room.filter(id=room_id).delete()
            return redirect(
                app.url_for("RoomsView"),
                status=204,
                headers={"HX-Location": app.url_for("RoomsView")},
            )

    @serializer(html)
    async def new_room(request: Request):
        page = Page(
            name="new_room",
            title="Nowy Pokój",
        )

        base_ctx = BaseContext(app=app, current_page=page)
        navbar = base_ctx.app_navbar

        page_content = BasePage(
            navbar,
            div(
                Breadcrumbs(
                    app, base_ctx.navigation["home"], base_ctx.navigation["rooms"], page
                ),
                class_name="w-full max-w-screen-xl mx-auto p-2",
            ),
            section(
                Room.get_form(),
                class_name="block w-full max-w-screen-xl mx-auto",
            ),
            title=page.title,
        )

        return page_content.render()

    @serializer(html)
    async def room_bulbs_state(request: Request, id: int):
        room = await Room.get(id=id).prefetch_related("bulbs")
        await room.assign_room_state()
        return RoomLightSwitch(app, room).render()

    async def change_room_brightness(request: Request, id: int):
        # room = await Room.get(id=id).prefetch_related("bulbs")
        # {
        #   'include-bulb-3': ['on'],
        #   'include-bulb-8': ['on'],
        #   'include-bulb-9': ['on'],
        #   'group_brightness': ['30'],
        #   'room_state_value': ['true'],
        #   'room_state': ['on']
        # }
        # TODO: parse included bulbs in some function, add validation
        included_bulb_prefix = "include-bulb-"
        bulb_ids = [
            int(key.replace(included_bulb_prefix, ""))
            for key in request.form.keys()
            if included_bulb_prefix in key
        ]
        brightness = int(request.form.get("group_brightness"))
        await change_brightness(bulb_ids, brightness)

        room = await Room.get(id=id).prefetch_related("bulbs")
        await room.assign_room_brightness()
        res = html(RoomBrightnessSlider(app, room).render())

        if len(bulb_ids) > 0:
            hx_trigger = "change-room-state"
            res.headers.add("HX-Trigger", hx_trigger)

        return res

    async def change_room_state(request: Request, id: int):
        # TODO: parse included bulbs in some function, add validation
        included_bulb_prefix = "include-bulb-"
        bulb_ids = [
            int(key.replace(included_bulb_prefix, ""))
            for key in request.form.keys()
            if included_bulb_prefix in key
        ]
        bulb_state = get_room_state_from_form(request.form)
        await toggle_state(bulb_ids, bulb_state)

        room = await Room.get(id=id).prefetch_related("bulbs")
        await room.assign_room_brightness()
        res = html(RoomBrightnessSlider(app, room).render())

        if len(bulb_ids) > 0:
            hx_trigger = "change-room-state"
            res.headers.add("HX-Trigger", hx_trigger)

        return res

    @serializer(html)
    async def room_bulbs_brightness(request: Request, id: int):
        room = await Room.get(id=id).prefetch_related("bulbs")
        await room.assign_room_brightness()
        return RoomBrightnessSlider(app, room).render()

    app.add_route(RoomView.as_view(), "/room")
    app.add_route(new_room, "rooms/new", methods=["GET"], name="new_room")
    app.add_route(
        change_room_brightness,
        "room/<id:int>/change-brightness",
        methods=["POST"],
    )
    app.add_route(
        room_bulbs_state,
        "room/<id:int>/bulbs-state",
        methods=["GET"],
        name=RoomLightSwitch.route,
    )
    app.add_route(
        room_bulbs_brightness,
        "room/<id:int>/bulbs-brightness",
        methods=["GET"],
        name=RoomBrightnessSlider.route,
    )
    #     TODO: refactor
    app.add_route(
        change_room_brightness,
        "room-brigthness/<id:int>",
        name="room-brigthness",
        methods=["POST"],
    )
    #     TODO: refactor
    app.add_route(
        change_room_state,
        "room-state/<id:int>",
        name="room-state",
        methods=["POST"],
    )
