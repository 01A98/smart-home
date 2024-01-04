from sanic import Request, Sanic
from sanic.views import HTTPMethodView
from sanic_ext import render

from .. import NAVIGATION, Page, PageContext


def create_view(app: Sanic) -> None:
    class HomeView(HTTPMethodView):
        page = Page(
            name="HomeView",
            title="Strona główna",
            template_path="views/home/get.html",
        )

        async def get(self, request: Request):
            return await render(
                self.page.template_path,
                context=PageContext(current_page=self.page).model_dump(),
            )

    app.add_route(HomeView.as_view(), "/")
    NAVIGATION["home"] = HomeView.page
