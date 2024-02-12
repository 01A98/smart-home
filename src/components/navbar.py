from __future__ import annotations

from typing import TYPE_CHECKING

from dominate.svg import svg, path
from dominate.tags import *
from sanic import Sanic

if TYPE_CHECKING:
    from ..views import Page


# noinspection PyStatementEffect
class navbar(html_tag):
    HIGHLIGHT_CLASS = "bg-blue-700 text-white md:text-blue-500 dark:md:text-blue-500"
    tagname = "app-navbar"

    def __init__(
        self,
        app: Sanic,
        navigation: dict[str, Page],
        current_page: Page,
    ) -> None:
        super().__init__()
        self.home_url = app.url_for("HomeView")
        self.navigation = navigation
        self.current_page = current_page

        self["x-data"] = f"""{{
                open: false,
                currentPageName: '{self.current_page.name if self.current_page else ""}'
            }}"""
        self["class"] = "w-full"

        with self:
            with nav(
                id="navbar",
                class_name="mx-auto flex w-full flex-col items-center "
                "border-gray-200 bg-gray-50 p-4 dark:bg-gray-900 "
                "md:flex-row md:px-8 md:py-4",
                **{"hx-preserve": "true"},
            ):
                with div(class_name="flex w-full flex-row justify-between"):
                    self.home_link()
                    self.open_menu_icon()
                    self.close_menu_icon()

                with ul(
                    id="menu-items",
                    class_name="mt-4 flex hidden w-full flex-col justify-center rounded-lg "
                    "border border-gray-300 bg-gray-50 p-4 font-medium "
                    "dark:border-gray-700 dark:bg-gray-800 md:mt-0 md:flex md:flex-row "
                    "md:space-x-8 md:border-0 md:p-0 md:dark:bg-gray-900",
                    **{
                        "x-bind:class": "{'hidden': !open}",
                    },
                ):
                    for page in self.navigation.values():
                        li(
                            a(
                                page.title,
                                pageName=page.name,
                                href=app.url_for(page.name),
                                class_name=f"""
                                        transition duration-200 hover:-translate-y-[2px] focus:ring-4 
                                        focus:outline-none focus:ring-primary-300 font-medium px-5 
                                        text-center dark:focus:ring-primary-900 block rounded py-2 
                                        text-gray-900 dark:text-white md:bg-transparent md:p-0 
                                        {self.HIGHLIGHT_CLASS if self.current_page and self.current_page.name == page.name else ''}
                                    """.strip(),
                                **{
                                    "x-bind:class": f"{{'{self.HIGHLIGHT_CLASS}': currentPageName === $el.getAttribute('pageName')}}"
                                },
                            ),
                        )

    def home_link(self) -> html_tag:
        with a(
            id="logo-link",
            href=self.home_url,
            **{
                "hx-boost": "false",
            },
        ):
            with svg(
                xmlns="http://www.w3.org/2000/svg",
                height="28",
                width="24",
                class_name="dark:fill-white fill-gray-700",
                viewBox="0 0 448 512",
            ):
                return path(
                    d="M349.4 44.6c5.9-13.7 1.5-29.7-10.6-38.5s-28.6-8-39.9 1.8l-256 224c-10 8.8-13.6 "
                    "22.9-8.9 35.3S50.7 288 64 288H175.5L98.6 467.4c-5.9 13.7-1.5 29.7 10.6 38.5s28.6 8 "
                    "39.9-1.8l256-224c10-8.8 13.6-22.9 8.9-35.3s-16.6-20.7-30-20.7H272.5L349.4 44.6z",
                )

    @staticmethod
    def open_menu_icon() -> html_tag:
        with svg(
            id="open-menu",
            xmlns="http://www.w3.org/2000/svg",
            height="2em",
            class_name="md:hidden transition-opacity hover:opacity-90 fill-gray-700 dark:fill-gray-200",
            viewBox="0 0 448 512",
            **{
                "x-on:click": "open = true",
                "x-show": "!open",
            },
        ):
            return path(
                d="M0 96C0 78.3 14.3 64 32 64H416c17.7 0 32 14.3 32 32s-14.3 32-32 32H32C14.3 128 0 113.7 0 96zM0 "
                "256c0-17.7 14.3-32 32-32H416c17.7 0 32 14.3 32 32s-14.3 32-32 32H32c-17.7 0-32-14.3-32-32zM448 "
                "416c0 17.7-14.3 32-32 32H32c-17.7 0-32-14.3-32-32s14.3-32 32-32H416c17.7 0 32 14.3 32 32z",
            )

    @staticmethod
    def close_menu_icon() -> html_tag:
        with svg(
            id="close-menu",
            xmlns="http://www.w3.org/2000/svg",
            height="2em",
            class_name="md:hidden transition-opacity hover:opacity-90 fill-gray-700 dark:fill-gray-200",
            viewBox="0 0 448 512",
            **{
                "x-on:click": "open = false",
                "x-show": "open",
                "x-cloak": "",
            },
        ):
            return path(
                d="M342.6 150.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L192 210.7 86.6 "
                "105.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3L146.7 256 41.4 361.4c-12.5 12.5-12.5 32.8 0 "
                "45.3s32.8 12.5 45.3 0L192 301.3 297.4 406.6c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L237.3 256 "
                "342.6 150.6z",
            )
