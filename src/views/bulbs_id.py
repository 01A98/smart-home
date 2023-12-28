from typing import Optional

from sanic import Request, Sanic
from sanic.views import HTTPMethodView
from tortoise.transactions import atomic

from ..models import Bulb, Bulb_Py
from . import Page, PageContext


def create_view(app: Sanic) -> None:
    class BulbView(HTTPMethodView):
        decorators = [atomic()]
        template_path = "views/bulbs/:id/get.html"

        @classmethod
        def page(cls, id: str):
            if id == "new":
                return Page(
                    name="bulb_handler",
                    path="/bulbs/new",
                    title="Dodaj Żarówkę",
                    template_path=cls.template_path,
                )
            else:
                id_ = int(id)
                return Page(
                    name="bulb_handler",
                    path=f"/bulbs/${id_}",
                    title=f"Żarówka #${id_}",
                    template_path=cls.template_path,
                )

        @app.ext.template(template_path)
        async def get(self, request: Request, id: str):
            context = PageContext(current_page=self.page(id)).model_dump()
            if id == "new":
                context["new"] = True
            else:
                id_ = int(id)
                bulb_record = await Bulb.get(id=id_)
                bulb = (await Bulb_Py.from_tortoise_orm(bulb_record)).model_dump()
                context["bulb"] = bulb

            return context

    app.add_route(BulbView.as_view(), "/bulb/<id:strorempty>", name="bulb_handler")
