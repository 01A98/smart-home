from sanic import BadRequest, Request, Sanic
from sanic.response import redirect
from sanic.views import HTTPMethodView
from tortoise.transactions import atomic

from ....form_helpers import get_choices, get_formdata
from ....forms import BulbForm
from ....models import Bulb, Room
from ... import Page, PageContext


def create_view(app: Sanic) -> None:
    class BulbView(HTTPMethodView):
        decorators = [atomic()]
        template_path = "views/bulbs/:id/get.html"

        @classmethod
        def page(cls, id: str):
            if id == "new":
                return Page(
                    name="bulb",
                    path="/bulbs/new",
                    title="Dodaj Żarówkę",
                    template_path=cls.template_path,
                )
            else:
                id_ = int(id)
                return Page(
                    name="bulb",
                    path=f"/bulbs/{id_}",
                    title=f"Żarówka #{id_}",
                    template_path=cls.template_path,
                )

        @app.ext.template(template_path)
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

            return dict(form=form, **context)

        async def post(self, request: Request, id: str):
            form = BulbForm(get_formdata(request))
            form.room.choices = get_choices(await Room.all(), "name")  # type: ignore

            if form.validate():
                await Bulb.create(
                    name=form.name.data,
                    ip=form.ip_address.data,
                )
                return redirect(app.url_for("bulbs"), status=303)
            if form.errors:
                raise BadRequest(str(form.errors.items()))

        async def patch(self, request: Request, id: str):
            form = BulbForm(get_formdata(request))
            form.room.choices = get_choices(await Room.all(), "name")  # type: ignore
            id_ = int(id)

            if form.validate():
                await Bulb.filter(id=id_).update(
                    name=form.name.data,
                    ip=form.ip_address.data,
                    room_id=form.room.data,
                )
                return redirect(app.url_for("bulbs"), status=303)
            if form.errors:
                raise BadRequest(str(form.errors.items()))

    app.add_route(BulbView.as_view(), "/bulbs/<id:strorempty>", name="bulb")
