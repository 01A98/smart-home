import random
from dataclasses import dataclass

from dominate import document
from dominate.tags import section, div
from sanic import Request, Sanic, html, json, redirect
from sanic.views import HTTPMethodView
from sanic_ext import serializer
from tortoise.transactions import atomic

from src.components.base_page import BasePage
from src.components.breadcrumbs import Breadcrumbs
from src.models.bulb import Bulb, BulbForm
from src.models.room import Room
from src.views import Page, BaseContext
from src.wiz import BulbParameters, WizMessage


@dataclass
class Routes:
    bulb_with_state: str = "bulb_with_state"


def create_view(app: Sanic) -> None:
    class BulbView(HTTPMethodView):
        decorators = [atomic()]

        @staticmethod
        async def post(request: Request):
            form = BulbForm(request.form)
            # TODO: move somewhere, figure out imports to avoid circ
            NO_ROOM_ID = "99999"

            if form.data.get("room_id") == NO_ROOM_ID:
                del form.room_id

            await Bulb.create(**form.data)
            return redirect(
                app.url_for("BulbsView"),
                status=204,
                headers={"HX-Location": app.url_for("BulbsView")},
            )

        @staticmethod
        async def patch(request: Request):
            bulb_id = request.args.get("id")
            form = BulbForm(request.form)
            # TODO: move somewhere, figure out imports to avoid circ
            NO_ROOM_ID = "99999"

            if form.data.get("room_id") == NO_ROOM_ID:
                form.room_id.data = None

            await Bulb.filter(id=bulb_id).update(**form.data)
            return redirect(
                app.url_for("BulbsView"),
                status=204,
                headers={"HX-Location": app.url_for("BulbsView")},
            )

        @staticmethod
        async def delete(request: Request):
            bulb_id = request.args.get("id")
            await Bulb.filter(id=bulb_id).delete()
            return redirect(
                app.url_for("BulbsView"),
                status=204,
                headers={
                    "HX-Refresh": "true",
                },
            )

    @serializer(html)
    @atomic()
    async def new_bulb(request: Request):
        page = Page(
            name="new_bulb",
            title="Nowa Żarówka",
        )

        rooms = await Room.all()
        bulb_form = Bulb.get_form({"hx-post": app.url_for("BulbView")}, rooms)
        view = _get_bulb_view(page, bulb_form)

        return view.render()

    @serializer(html)
    @atomic()
    async def edit_bulb(request: Request, bulb_id: int):
        page = Page(
            name="edit_bulb",
            title="Edytuj Żarówkę",
        )

        rooms = await Room.all()
        bulb = await Bulb.get(id=bulb_id)
        bulb_form = Bulb.get_form(
            {"hx-patch": app.url_for("BulbView", id=bulb.id)}, rooms, bulb
        )
        view = _get_bulb_view(page, bulb_form)

        return view.render()

    def _get_bulb_view(page, bulb_form: BulbForm) -> document:
        base_ctx = BaseContext(app=app, current_page=page)
        navbar = base_ctx.app_navbar
        page_content = BasePage(
            navbar,
            div(
                Breadcrumbs(
                    app, base_ctx.navigation["home"], base_ctx.navigation["bulbs"], page
                ),
                class_name="w-full max-w-screen-xl mx-auto p-2",
            ),
            section(
                bulb_form,
                class_name="block w-full max-w-screen-xl mx-auto",
            ),
            title=page.title,
        )
        return page_content

    # TODO: add option for room view alongside other inputs
    async def pick_random_color(request: Request, id: int):
        bulb = await Bulb.get(id=id)
        await bulb.send_message(
            WizMessage(
                params=BulbParameters(
                    state=True,
                    red=random.randint(0, 255),
                    green=random.randint(0, 255),
                    blue=random.randint(0, 255),
                )
            )
        )
        return json(
            bulb.wiz_info,
            headers={"HX-Trigger": f"reload-bulb-{bulb.id}-control-form"},
        )

    app.add_route(BulbView.as_view(), "/bulb")
    app.add_route(new_bulb, "bulbs/new", methods=["GET"], name="new_bulb")
    app.add_route(
        edit_bulb, "bulbs/edit/<bulb_id:int>", methods=["GET"], name="edit_bulb"
    )

    app.add_route(
        pick_random_color,
        "bulbs/<id:int>/pick-random-color",
        name="pick_random_color",
        methods=["POST"],
    )
