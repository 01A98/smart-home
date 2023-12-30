from sanic import BadRequest, Request, Sanic
from sanic.response import redirect
from sanic.views import HTTPMethodView
from tortoise.transactions import atomic

from ..form_helpers import get_formdata
from ..forms import RoomForm
from ..models import Room, Room_Py
from . import Page, PageContext


def create_view(app: Sanic) -> None:
    class RoomView(HTTPMethodView):
        decorators = [atomic()]
        template_path = "views/rooms/:id/get.html"

        @classmethod
        def page(cls, id: str):
            if id == "new":
                return Page(
                    name="room",
                    path="/rooms/new",
                    title="Dodaj Pokój",
                    template_path=cls.template_path,
                )
            else:
                id_ = int(id)
                return Page(
                    name="room",
                    path=f"/rooms/${id_}",
                    title=f"Pokój #${id_}",
                    template_path=cls.template_path,
                )

        @app.ext.template(template_path)
        async def get(self, request: Request, id: str):
            context = PageContext(current_page=self.page(id)).model_dump()
            if id == "new":
                context["new"] = True
            else:
                id_ = int(id)
                room_record = await Room.get(id=id_)
                room = (await Room_Py.from_tortoise_orm(room_record)).model_dump()
                context["room"] = room

            return {**context, "form": RoomForm()}

        async def post(self, request: Request, id: str):
            form = RoomForm(get_formdata(request))
            if form.validate():
                await Room.create(
                    name=form.name.data,
                    description=form.description.data,
                )
                return redirect(app.url_for("rooms"), status=303)
            if form.errors:
                raise BadRequest(str(form.errors.items()))

    app.add_route(RoomView.as_view(), "/room/<id:strorempty>", name="room")
