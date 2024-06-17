from __future__ import annotations

from typing import TYPE_CHECKING, List

from dominate.tags import nav, a, ol, li, span
from sanic import Sanic

from src.components.material_icons import Icon

if TYPE_CHECKING:
    from src.views import Page


# noinspection PyStatementEffect
class Breadcrumbs(nav):
    tagname = "nav"
    id = "app-breadcrumbs"
    app: Sanic
    pages: List[Page]

    def __init__(
        self,
        app: Sanic,
        *pages: Page,
    ) -> None:
        super().__init__()
        self.app = app
        self.pages = list(pages)

        self["class"] = "block w-fit"
        self["aria-label"] = "breadcrumb"

        with self:
            with ol(
                class_name="flex flex-wrap items-center w-full px-4 py-2 rounded-md bg-blue-gray-50 bg-opacity-60"
            ) as _ol:
                _ol.add(self.list_items)

    @property
    def list_items(self) -> list[li]:
        list_items = []
        li_class = (
            "flex items-center justify-center font-sans text-sm antialiased font-normal leading-normal "
            "transition-colors duration-300 cursor-pointer text-blue-gray-900 hover:text-light-blue-500"
        )

        for ix, page in enumerate(self.pages):
            if ix == len(self.pages) - 1:
                with li(class_name=li_class, aria_current="page") as _li:
                    a(
                        page.title,
                        href=self.app.url_for(page.name),
                        class_name="opacity-60",
                    )
                list_items.append(_li)
            else:
                with li(class_name=li_class) as _li:
                    with a(
                        href=self.app.url_for(page.name),
                    ):
                        with span(
                            class_name="flex items-center transition-colors hover:text-blue-500"
                        ) as span_:
                            if ix == 0:
                                Icon("home")
                            else:
                                span_.add(page.title)

                    span(
                        Icon("chevron_right"),
                        class_name="mx-2 font-sans text-sm antialiased font-normal leading-normal pointer-events-none "
                        "select-none text-blue-gray-500 flex items-center",
                    )
                    list_items.append(_li)

        return list_items

    @property
    def breadcrumb_slash(self):
        return span(
            "/",
            class_name="mx-2 font-sans text-sm antialiased font-normal leading-normal pointer-events-none select-none "
            "text-blue-gray-500",
        )
