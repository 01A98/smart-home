import random

from sanic import BadRequest, Request, Sanic, html, json, text
from sanic.response import redirect
from sanic.views import HTTPMethodView
from sanic_ext import render
from tortoise.transactions import atomic

from ... import Page, PageContext
from ....forms.bulb import BulbDetailsForm, bulb_control_form_factory
from ....forms.helpers import (
    get_choices,
    get_formdata,
    coerce_literal_bool_to_bool,
    coerce_rgb_string_to_tuple,
)
from ....models.bulb import Bulb
from ....models.room import Room
from ....wiz import BulbParameters, WizMessage


def create_view(app: Sanic) -> None:
    class BulbView(HTTPMethodView):
        decorators = [atomic()]
        template_path = "views/bulbs/:id/get.html"

        @classmethod
        def page(cls, id: str):
            if id == "new":
                return Page(
                    name="BulbView",
                    title="Dodaj Żarówkę",
                    template_path=cls.template_path,
                )
            else:
                id_ = int(id)
                return Page(
                    name="BulbView",
                    title=f"Żarówka #{id_}",
                    template_path=cls.template_path,
                )

        async def get(self, request: Request, id: str):
            context = PageContext(current_page=self.page(id)).model_dump()
            details_form = BulbDetailsForm()
            choices = get_choices(await Room.all(), "name")
            details_form.room.choices = choices  # type: ignore

            if id == "new":
                context["new"] = True
            else:
                id_ = int(id)
                bulb = await Bulb.get(id=id_).prefetch_related("room")
                await bulb.assign_wiz_info()

                details_form.name.default = bulb.name
                details_form.ip_address.default = bulb.ip
                details_form.room.default = bulb.room_id
                details_form.process()

                context["bulb"] = bulb

                BulbControlForm = bulb_control_form_factory(bulb, app)
                control_form = BulbControlForm()
                context["control_form"] = control_form

            return await render(
                self.template_path,
                context=dict(details_form=details_form, **context),
            )

        @staticmethod
        async def post(request: Request, id: str):
            form = BulbDetailsForm(get_formdata(request))
            form.room.choices = get_choices(await Room.all(), "name")  # type: ignore

            if form.validate():
                await Bulb.create(
                    name=form.name.data,
                    ip=form.ip_address.data,
                )
                return redirect(app.url_for("BulbsView"), status=303)
            if form.errors:
                raise BadRequest(str(form.errors.items()))

        @staticmethod
        async def patch(request: Request, id: str):
            form = BulbDetailsForm(get_formdata(request))
            form.room.choices = get_choices(await Room.all(), "name")  # type: ignore
            id_ = int(id)

            if form.validate():
                await Bulb.filter(id=id_).update(
                    name=form.name.data,
                    ip=form.ip_address.data,
                    room_id=form.room.data,
                )
                return redirect(app.url_for("BulbsView"), status=303)
            if form.errors:
                raise BadRequest(str(form.errors.items()))

        @staticmethod
        async def delete(request: Request, id: str):
            id_ = int(id)
            await Bulb.filter(id=id_).delete()
            return redirect(app.url_for("BulbsView"), status=303)

    async def get_bulb_with_wiz_info(request: Request, id: int):
        bulb = await Bulb.get(id=id)

        await bulb.assign_wiz_info()

        context = dict(bulb=bulb)
        context["bulb_icon"] = generate_bulb_icon(bulb)
        context["with_name"] = request.args.get("with_name", False)

        return await render("views/bulbs/:id/bulb-info.html", context=context)

    async def control_bulb(request: Request, id: int):
        bulb = await Bulb.get(id=id)
        BulbControlForm = bulb_control_form_factory(bulb, app)
        control_form = BulbControlForm(get_formdata(request))

        if request.method == "POST":
            if control_form.validate():
                previous_state = coerce_literal_bool_to_bool(
                    control_form.previous_state.data
                )
                if (
                    previous_state == control_form.updated_state.data
                    and control_form.updated_state.data is False
                ):
                    return text("No changes", headers={"HX-Reswap": "none"}, status=204)

                red, green, blue = coerce_rgb_string_to_tuple(control_form.color.data)

                await bulb.send_message(
                    WizMessage(
                        params=BulbParameters(
                            state=control_form.updated_state.data,
                            red=red,
                            green=green,
                            blue=blue,
                            brightness=control_form.brightness.data,
                            temperature=control_form.temperature.data,
                        )
                    )
                )

                await bulb.assign_wiz_info()

                return await render(
                    "views/bulbs/:id/bulb-control-form.html",
                    headers={"HX-Trigger-After-Settle": f"reload-bulb-{id}-control"},
                    context=dict(
                        bulb=bulb,
                        control_form=await _process_control_form(bulb, request),
                    ),
                )

            if control_form.errors:
                raise BadRequest(str(control_form.errors.items()))
        if request.method == "GET":
            await bulb.assign_wiz_info()
            return await render(
                "views/bulbs/:id/bulb-control-form.html",
                context=dict(
                    bulb=bulb,
                    control_form=await _process_control_form(bulb, request),
                ),
            )

    async def _process_control_form(bulb, request):
        BulbControlForm = bulb_control_form_factory(bulb, app)
        control_form = BulbControlForm(get_formdata(request))
        control_form.previous_state.default = (
            "True" if bulb.wiz_info["state"] else "False"
        )
        control_form.updated_state.default = bulb.wiz_info["state"]
        control_form.process()
        return control_form

    async def toggle_bulb_state(request: Request, id: int):
        # TODO: this is outdated now, make consistent with other forms
        previous_state = request.form.get("bulb_state_value")
        updated_state = request.form.get("bulb_state", default=None)
        bulb_state = None

        if previous_state is not None and updated_state is None:
            bulb_state = not previous_state
        if previous_state == "False" and updated_state is not None:
            bulb_state = True

        bulb = await Bulb.get(id=id)
        if bulb_state is not None:
            await bulb.toggle_state(bulb_state)
        else:
            await bulb.assign_wiz_info()

        return await render(
            "views/bulbs/:id/bulb-state-toggle-form.html",
            headers={"HX-Trigger-After-Settle": f"reload-bulb-{id}-icon"},
            context=dict(bulb=bulb),
        )

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

    async def get_bulb_icon(request: Request, id: int):
        bulb = await Bulb.get(id=id)
        await bulb.assign_wiz_info()
        return html(generate_bulb_icon(bulb))

    def generate_bulb_icon(bulb: Bulb) -> str:
        is_offline = bulb.wiz_info is None or bulb.wiz_info == "Bulb offline"
        if is_offline:
            return """
                <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 fill-white" viewBox="0 0 512 512">
                    <!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2024 Fonticons, Inc.-->
                    <path d="M288 32c0-17.7-14.3-32-32-32s-32 14.3-32 32V256c0 17.7 14.3 32 32 32s32-14.3 32-32V32zM143.5 120.6c13.6-11.3 15.4-31.5 4.1-45.1s-31.5-15.4-45.1-4.1C49.7 115.4 16 181.8 16 256c0 132.5 107.5 240 240 240s240-107.5 240-240c0-74.2-33.8-140.6-86.6-184.6c-13.6-11.3-33.8-9.4-45.1 4.1s-9.4 33.8 4.1 45.1c38.9 32.3 63.5 81 63.5 135.4c0 97.2-78.8 176-176 176s-176-78.8-176-176c0-54.4 24.7-103.1 63.5-135.4z"></path>
                </svg>
            """

        fill_color = "yellow-400"
        if not bulb.wiz_info["state"]:
            fill_color = "gray-400"

        return f"""
            <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-6 h-6 fill-{fill_color}"
                viewBox="0 0 384 512"
            >
                <!--!Font Awesome Free 6.5.1 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2023 Fonticons, Inc.-->
                <path d="M272 384c9.6-31.9 29.5-59.1 49.2-86.2l0 0c5.2-7.1 10.4-14.2 15.4-21.4c19.8-28.5 31.4-63 31.4-100.3C368 78.8 289.2 0 192 0S16 78.8 16 176c0 37.3 11.6 71.9 31.4 100.3c5 7.2 10.2 14.3 15.4 21.4l0 0c19.8 27.1 39.7 54.4 49.2 86.2H272zM192 512c44.2 0 80-35.8 80-80V416H112v16c0 44.2 35.8 80 80 80zM112 176c0 8.8-7.2 16-16 16s-16-7.2-16-16c0-61.9 50.1-112 112-112c8.8 0 16 7.2 16 16s-7.2 16-16 16c-44.2 0-80 35.8-80 80z"></path>
            </svg>
        """

    app.add_route(BulbView.as_view(), "/bulbs/<id:strorempty>")
    app.add_route(
        control_bulb,
        "/bulbs/<id:int>/control",
        name="bulb_control",
        methods=["POST", "GET"],
    )
    app.add_route(
        get_bulb_with_wiz_info,
        "bulbs/<id:int>/wiz-info",
        name="bulb_with_wiz_info",
    )
    app.add_route(
        toggle_bulb_state,
        "bulbs/<id:int>/toggle-state",
        name="toggle_bulb_state",
        methods=["POST"],
    )
    app.add_route(
        pick_random_color,
        "bulbs/<id:int>/pick-random-color",
        name="pick_random_color",
        methods=["POST"],
    )
    app.add_route(
        get_bulb_icon,
        "bulbs/<id:int>/icon",
        name="get_bulb_icon",
    )
