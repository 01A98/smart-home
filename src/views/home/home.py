from sanic import Request, Sanic, redirect
from sanic.views import HTTPMethodView

from .. import Page, NAVIGATION


def create_view(app: Sanic) -> None:
    class HomeView(HTTPMethodView):
        page = Page(
            name="HomeView",
            title="Strona główna",
            template_path="views/home/get.html",
        )

        async def get(self, request: Request):
            return redirect(app.url_for("RoomsView"), status=303)

    app.add_route(HomeView.as_view(), "/")
    NAVIGATION["home"] = HomeView.page
