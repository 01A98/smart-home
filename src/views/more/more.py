from dominate.tags import section, div, h1, h3, p, a
from sanic import Request, Sanic, html
from sanic.views import HTTPMethodView
from sanic_ext import serializer

from src.components.breadcrumbs import Breadcrumbs
from src.views import NAVIGATION, Page, BaseContext
from src.components.base_page import BasePage


def create_view(app: Sanic) -> None:
    class MoreView(HTTPMethodView):
        decorators = [serializer(html)]

        page = Page(
            name="MoreView",
            title="Więcej",
            template_path="views/more/get.html",
        )

        async def get(self, request: Request):
            base_ctx = BaseContext(app=app, current_page=self.page)
            navbar = base_ctx.app_navbar

            return BasePage(
                navbar,
                div(
                    Breadcrumbs(app, base_ctx.navigation["home"], self.page),
                    class_name="w-full max-w-screen-xl mx-auto p-2",
                ),
                section(
                    div(
                        h1(
                            "404",
                            class_name="text-7xl tracking-tight font-extrabold lg:text-9xl text-gray-900",
                        ),
                        h3(
                            "Nic tu nie ma :/",
                            class_name="mb-4 text-3xl tracking-tight font-bold text-gray-900 md:text-4xl",
                        ),
                        p(
                            "Może kiedyś będzie, tymczasem wróć do strony głównej.",
                            class_name="mb-4 text-lg font-light text-gray-500  mx-4",
                        ),
                        a(
                            "Do strony głównej",
                            href=app.url_for("HomeView"),
                            class_name="inline-flex text-gray:800 bg-primary-600 hover:bg-primary-800 "
                            "border border-gray focus:ring-4 focus:outline-none focus:ring-primary-300 font-medium "
                            "rounded-lg text-sm px-5 py-2.5 my-4 transition duration-200 hover:-translate-y-[2px]",
                        ),
                        class_name="my-4 mx-auto max-w-screen-sm flex flex-col gap-2 justify-center items-center",
                    ),
                    class_name="w-full h-full",
                ),
            ).render()

    app.add_route(MoreView.as_view(), "/more")
    NAVIGATION["more"] = MoreView.page
