from sanic import Request, Sanic
from sanic.views import HTTPMethodView
from tortoise.transactions import atomic

from ..models import Bulb, Bulb_Py
from . import NAVIGATION, Page, PageContext


def create_view(app: Sanic) -> None:
    class BulbsView(HTTPMethodView):
        decorators = [atomic()]
        page = Page(
            name="bulbs_handler",
            path="/bulbs",
            title="Żarówki",
            template_path="views/bulbs/get.html",
        )

        @app.ext.template(page.template_path)
        async def get(self, request: Request):
            bulbs = [
                (await Bulb_Py.from_tortoise_orm(bulb)).model_dump()
                for bulb in await Bulb.all()
            ]
            return {"bulbs": bulbs, **PageContext(current_page=self.page).model_dump()}

    app.add_route(BulbsView.as_view(), BulbsView.page.path, name=BulbsView.page.name)
    NAVIGATION["bulbs"] = BulbsView.page
