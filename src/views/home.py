from sanic import Request, Sanic
from sanic.views import HTTPMethodView

from ..utils import get_js_file
from . import NAVIGATION, Page, PageContext


def create_view(app: Sanic) -> None:
    class HomeView(HTTPMethodView):
        page = Page(
            name="home",
            path="/",
            title="Strona główna",
            template_path="views/home/get.html",
            js_file=get_js_file("views/home/index.ts"),
        )

        @app.ext.template(page.template_path)
        async def get(self, request: Request):
            return PageContext(current_page=self.page).model_dump()

    app.add_route(HomeView.as_view(), HomeView.page.path, name=HomeView.page.name)
    NAVIGATION["home"] = HomeView.page
