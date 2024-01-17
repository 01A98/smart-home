import random

from sanic import BadRequest, Request, Sanic, html, json, text
from sanic.response import redirect
from sanic.views import HTTPMethodView
from sanic_ext import render, serializer
from tortoise.transactions import atomic

from ... import Page, BaseContext
from ....components import bulb_icon
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
            context = BaseContext(app=app, current_page=self.page(id)).model_dump()
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
        context["bulb_icon"] = bulb_icon(bulb=bulb)
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

    @serializer(html)
    async def get_bulb_icon(request: Request, id: int):
        bulb = await Bulb.get(id=id)
        await bulb.assign_wiz_info()
        return str(bulb_icon(bulb=bulb))

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
