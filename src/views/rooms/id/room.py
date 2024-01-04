from sanic import BadRequest, Request, Sanic
from sanic.response import redirect
from sanic.views import HTTPMethodView
from tortoise.transactions import atomic

from ... import Page, PageContext
from ....forms.helpers import get_formdata
from ....forms.room import RoomForm
from ....models.room import Room


def create_view(app: Sanic) -> None:
    class RoomView(HTTPMethodView):
        decorators = [atomic()]
        template_path = "views/rooms/:id/get.html"

        @classmethod
        def page(cls, id: str):
            if id == "new":
                return Page(
                    name="RoomView",
                    title="Dodaj Pokój",
                    template_path=cls.template_path,
                )
            else:
                id_ = int(id)
                return Page(
                    name="RoomView",
                    title=f"Pokój #{id_}",
                    template_path=cls.template_path,
                )

        @app.ext.template(template_path)
        async def get(self, request: Request, id: str):
            context = PageContext(current_page=self.page(id)).model_dump()
            form = RoomForm()
            if id == "new":
                context["new"] = True
            else:
                id_ = int(id)
                room = await Room.get(id=id_)
                form.name.default = room.name
                form.description.default = room.description
                form.process()
                context["room"] = room

            return dict(form=form, **context)

        @staticmethod
        async def post(request: Request, id: str):
            form = RoomForm(get_formdata(request))
            if form.validate():
                await Room.create(
                    name=form.name.data,
                    description=form.description.data,
                )
                return redirect(app.url_for("RoomsView"), status=303)
            if form.errors:
                raise BadRequest(str(form.errors.items()))

    app.add_route(RoomView.as_view(), "/rooms/<id:strorempty>")
