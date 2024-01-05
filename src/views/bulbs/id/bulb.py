from sanic import BadRequest, Request, Sanic
from sanic.response import redirect
from sanic.views import HTTPMethodView
from sanic_ext import render
from tortoise.transactions import atomic

from ... import Page, PageContext
from ....forms.bulb import BulbForm
from ....forms.helpers import get_choices, get_formdata
from ....models.bulb import Bulb
from ....models.room import Room


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
            form = BulbForm()
            choices = get_choices(await Room.all(), "name")
            form.room.choices = choices  # type: ignore

            if id == "new":
                context["new"] = True
            else:
                id_ = int(id)
                bulb = await Bulb.get(id=id_).prefetch_related("room")

                form.name.default = bulb.name
                form.ip_address.default = bulb.ip
                form.room.default = bulb.room_id
                form.process()

                context["bulb"] = bulb

            return await render(
                self.template_path,
                context=dict(form=form, **context),
            )

        @staticmethod
        async def post(request: Request, id: str):
            form = BulbForm(get_formdata(request))
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
            form = BulbForm(get_formdata(request))
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
        context["with_name"] = request.args.get("with_name", False)

        return await render("views/bulbs/:id/bulb-info.html", context=context)

    async def toggle_bulb_state(request: Request, id: int):
        state = request.form.get("bulb_state_value")
        bulb_state = None
        if state == "True":
            bulb_state = True
        elif state == "False":
            bulb_state = False

        bulb = await Bulb.get(id=id)
        await bulb.toggle_state(not bulb_state)
        return await render(
            "views/bulbs/:id/bulb-state-toggle-form.html", context=dict(bulb=bulb)
        )

    app.add_route(BulbView.as_view(), "/bulbs/<id:strorempty>")
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
