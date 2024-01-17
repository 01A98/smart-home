from sanic import Request, Sanic
from sanic.views import HTTPMethodView
from sanic_ext import render

from .. import NAVIGATION, Page, BaseContext


def create_view(app: Sanic) -> None:
    class MoreView(HTTPMethodView):
        page = Page(
            name="MoreView",
            title="Więcej",
            template_path="views/more/get.html",
        )

        async def get(self, request: Request):
            return await render(
                self.page.template_path,
                context=BaseContext(app=app, current_page=self.page).model_dump(),
            )

    app.add_route(MoreView.as_view(), "/more")
    NAVIGATION["more"] = MoreView.page
