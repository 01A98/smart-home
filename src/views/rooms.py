from sanic import Request, Sanic
from sanic.views import HTTPMethodView
from tortoise.transactions import atomic

from ..models import Room, Room_Py
from . import NAVIGATION, Page, PageContext


def create_view(app: Sanic) -> None:
    class RoomsView(HTTPMethodView):
        decorators = [atomic()]
        page = Page(
            name="rooms",
            path="/rooms",
            title="Pokoje",
            template_path="views/rooms/get.html",
        )

        @app.ext.template(page.template_path)
        async def get(self, request: Request):
            rooms = [
                (await Room_Py.from_tortoise_orm(room)).model_dump()
                for room in await Room.all()
            ]
            return {"rooms": rooms, **PageContext(current_page=self.page).model_dump()}

    app.add_route(RoomsView.as_view(), RoomsView.page.path, name=RoomsView.page.name)
    NAVIGATION["rooms"] = RoomsView.page
