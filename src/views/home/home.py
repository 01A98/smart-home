from sanic import Request, Sanic
from sanic.views import HTTPMethodView
from sanic_ext import render

from .. import Page, NAVIGATION, BaseContext


def create_view(app: Sanic) -> None:
    class HomeView(HTTPMethodView):
        page = Page(
            name="HomeView",
            title="Strona główna",
            template_path="views/home/get.html",
        )

        async def get(self, request: Request):
            page_context = BaseContext(app=app, current_page=self.page)
            return await render(
                self.page.template_path,
                context=page_context.model_dump(),
            )

    app.add_route(HomeView.as_view(), "/")
    NAVIGATION["home"] = HomeView.page
