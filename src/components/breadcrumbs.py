from __future__ import annotations

from typing import TYPE_CHECKING

from dominate.svg import svg, path
from dominate.tags import nav, html_tag, a, ol, li, div, span
from sanic import Sanic

if TYPE_CHECKING:
    from views import Page


# noinspection PyStatementEffect
class breadcrumbs(html_tag):
    HIGHLIGHT_CLASS = "bg-blue-700 text-white md:text-blue-500 dark:md:text-blue-500"
    tagname = "app-breadcrumbs"
    app: Sanic
    pages: list[Page]

    def __init__(
        self,
        app: Sanic,
        *pages: Page,
    ) -> None:
        super().__init__()
        self.app = app
        self.pages = list(pages)
        self["class"] = "w-full"

        with self:
            with nav(
                class_name="mx-auto flex w-full flex-col shadow-md items-center border-gray-200 bg-gray-50 p-4 "
                "dark:bg-gray-900 md:flex-row md:px-8 md:py-4",
                aria_label="Breadcrumb",
            ):
                with ol(
                    class_name="inline-flex items-center space-x-1 md:space-x-2"
                ) as _ol:
                    _ol.add(self.list_items)

    @property
    def list_items(self) -> list[li]:
        list_items = []

        for ix, page in enumerate(self.pages):
            if ix == 0:
                with li() as _li:
                    a(
                        page.title,
                        href=self.app.url_for(page.name),
                        class_name="ms-1 text-sm font-medium text-gray-700 hover:text-blue-600 md:ms-2 "
                        "dark:text-gray-400 dark:hover:text-white",
                    )
                list_items.append(_li)
            elif ix == len(self.pages) - 1:
                with li(aria_current="page") as _li:
                    with div(class_name="flex items-center"):
                        self.arrow_svg
                        span(
                            page.title,
                            class_name="ms-1 text-sm font-medium text-gray-500 md:ms-2 dark:text-gray-400",
                        )
                list_items.append(_li)
            else:
                with li() as _li:
                    with div(class_name="flex items-center"):
                        self.arrow_svg
                        a(
                            page.title,
                            href=self.app.url_for(page.name),
                            class_name="ms-1 text-sm font-medium text-gray-700 hover:text-blue-600 md:ms-2 "
                            "dark:text-gray-400 dark:hover:text-white",
                        )
                list_items.append(_li)

        return list_items

    @property
    def arrow_svg(self):
        with svg(
            aria_hidden="true",
            xmlns="http://www.w3.org/2000/svg",
            fill="none",
            viewBox="0 0 6 10",
            class_name="w-3 h-3 text-gray-400 mx-1",
        ):
            return path(
                stroke="currentColor",
                stroke_linecap="round",
                stroke_linejoin="round",
                stroke_width="2",
                d="m1 9 4-4-4-4",
            )
