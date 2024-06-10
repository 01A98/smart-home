from typing import Literal

from dominate.svg import svg, circle
from dominate.tags import div, section, span, nav, ul, li, p
from sanic import Request, Sanic, html
from sanic.views import HTTPMethodView
from sanic_ext import serializer
from tortoise.transactions import atomic

from src.components.base_page import BasePage
from src.components.breadcrumbs import Breadcrumbs
from src.components.material_icons import Icon
from src.components.new_item_button import NewItemButton
from src.components.spinner import Spinner
from src.models.bulb import Bulb
from src.views import NAVIGATION, Page, BaseContext


def create_view(app: Sanic) -> None:
    class BulbsView(HTTPMethodView):
        decorators = [atomic(), serializer(html)]
        page = Page(
            name="BulbsView",
            title="Żarówki",
        )

        async def get(self, request: Request):
            bulbs = await Bulb.all().prefetch_related("room")

            base_ctx = BaseContext(app=app, current_page=self.page)
            navbar = base_ctx.app_navbar

            page_content = BasePage(
                navbar,
                div(
                    Breadcrumbs(app, base_ctx.navigation["home"], self.page),
                    class_name="w-full max-w-screen-xl mx-auto p-2",
                ),
                section(
                    div(
                        NewItemButton(href=app.url_for("BulbView", id="new")),
                        class_name="flex flex-row justify-between items-end w-full h-full my-4 mx-auto px-2",
                    ),
                    bulbs_list(bulbs, app),
                    class_name="block w-full max-w-screen-xl mx-auto",
                ),
                title=self.page.title,
            )

            return page_content.render()

    async def get_bulb_state_indicator(request: Request, id: int):
        type_: Literal["color"] | None = request.args.get("type")
        bulb = await Bulb.get(id=id)
        await bulb.assign_wiz_info()

        state = None
        if bulb.wiz_info and type(bulb.wiz_info.state) is bool:
            state = bulb.wiz_info.state

        content = svg(height=40, width=40, xmlns="http://www.w3.org/2000/svg")
        circle_ = circle(r="5", cx="20", cy="20")
        if type_ == "color":
            if state is True:
                circle_["fill"] = "#90ee90"
            elif state is False:
                circle_["fill"] = "#d1001f"
            else:
                circle_["fill"] = "gray"
        content.add(circle_)

        return html(content.render())

    app.add_route(BulbsView.as_view(), "/bulbs")
    app.add_route(
        get_bulb_state_indicator, "/bulb_state/<id:int>", name="bulb_state_indicator"
    )
    NAVIGATION["bulbs"] = BulbsView.page


def bulbs_list(bulbs: list[Bulb], app: Sanic) -> nav:
    with nav(
        class_name="w-5/6 h-full my-6 mx-auto rounded-md gap-1 "
        "font-sans text-blue-gray-700 shadow-md border border-gray-100"
    ) as nav_:
        with ul(class_name="w-full flex flex-col"):
            for bulb in bulbs:
                with li(
                    class_name="w-full flex flex-row items-center justify-between rounded-md p-3 "
                    "hover:bg-blue-500 hover:bg-opacity-80 hover:text-white focus:bg-blue-500 "
                    "focus:bg-opacity-80 focus:text-white active:bg-blue-gray-50 "
                ):
                    Icon("lightbulb", class_name="material-symbols-rounded")
                    p(bulb.name, class_name="text-xs")
                    span(
                        bulb.ip,
                        role="button",
                        class_name="px-2 py-1 font-sans text-xs font-bold text-gray-900 bg-gray-100 uppercase "
                        "rounded-full",
                    )
                    div(
                        Spinner(htmx_indicator=True),
                        class_name="w-full",
                        **{
                            # TODO: change to constant url
                            "hx-get": f"/bulb_state/{bulb.id}?type=color",
                            "hx-swap": "outerHTML",
                            "hx-trigger": "load",
                        },
                    )
    return nav_
