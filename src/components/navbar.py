from __future__ import annotations

from typing import TYPE_CHECKING

from dominate.svg import svg, path
from dominate.tags import *
from sanic import Sanic

if TYPE_CHECKING:
    from ..views import Page


class Navbar(nav):
    tagname = "nav"
    id = "app-navbar"

    def __init__(
            self,
            app: Sanic,
            navigation: dict[str, Page],
            current_page: Page,
    ) -> None:
        super().__init__()
        self.app = app
        self.navigation = navigation
        self.current_page = current_page

        self["class"] = ("block w-full max-w-screen-xl px-6 py-3 mx-auto text-white bg-white border shadow-md "
                         "rounded-xl border-white/80 bg-opacity-80 backdrop-blur-2xl backdrop-saturate-200")

        with self:
            with div(class_name="flex items-center justify-between text-blue-gray-900"):
                self.home_link()
                with div(class_name="hidden md:block"):
                    with ul(class_name="flex gap-2 my-2 md:mb-0 md:mt-0 md:flex-row md:items-center md:gap-6"):
                        for page in self.navigation.values():
                            self.navbar_page_link(page)

                with button(
                        class_name="relative ml-auto inline-block h-10 max-h-[40px] w-10 max-w-[40px] select-none "
                                   "rounded-lg text-center align-middle font-sans text-xs font-medium uppercase "
                                   "text-gray-900 transition-all hover:bg-gray-900/10 active:bg-gray-900/20 "
                                   "disabled:pointer-events-none disabled:opacity-50 disabled:shadow-none md:hidden",
                        type="button",
                        data_ripple_dark="true",
                        data_ripple_light="true",
                        data_collapse_target="navbar"
                ):
                    self.hamburger_icon()

            with div(
                    class_name="block h-0 w-full basis-full overflow-hidden transition-all duration-300 ease-in "
                               "md:hidden",
                    data_collapse="navbar"
            ):

                with ul(
                        class_name="flex flex-col gap-4",
                ):
                    hr(class_name="border-t border-gray-100 mt-4")
                    for page in self.navigation.values():
                        self.navbar_page_link(page)

    def navbar_page_link(self, page: Page) -> html_tag:
        with li(class_name="block p-1 font-sans text-sm antialiased font-medium leading-normal text-blue-gray-900"):
            return a(
                page.title,
                pageName=page.name,
                href=self.app.url_for(page.name),
                class_name="flex items-center transition-colors hover:text-blue-500",
            )

    def home_link(self) -> html_tag:
        with a(
                id="logo-link",
                href=self.app.url_for("HomeView"),
                class_name="mr-4 block cursor-pointer py-1.5 font-sans text-base font-semibold leading-relaxed "
                           "tracking-normal text-inherit antialiased",
                **{
                    "hx-boost": "false",
                },
        ):
            with svg(
                    xmlns="http://www.w3.org/2000/svg",
                    height="28",
                    width="24",
                    class_name="fill-gray-700",
                    viewBox="0 0 448 512",
            ):
                return path(
                    d="M349.4 44.6c5.9-13.7 1.5-29.7-10.6-38.5s-28.6-8-39.9 1.8l-256 224c-10 8.8-13.6 "
                      "22.9-8.9 35.3S50.7 288 64 288H175.5L98.6 467.4c-5.9 13.7-1.5 29.7 10.6 38.5s28.6 8 "
                      "39.9-1.8l256-224c10-8.8 13.6-22.9 8.9-35.3s-16.6-20.7-30-20.7H272.5L349.4 44.6z",
                )

    @staticmethod
    def hamburger_icon() -> html_tag:
        with span(
                class_name="absolute top-1/2 left-1/2 transform -translate-y-1/2 -translate-x-1/2",
        ):
            with svg(
                    xmlns="http://www.w3.org/2000/svg",
                    fill="none",
                    viewBox="0 0 24 24",
                    stroke_width="2",
                    stroke="currentColor",
                    aria_hidden="true",
                    class_name="w-6 h-6"
            ):
                return path(
                    stroke_linecap="round",
                    stroke_linejoin="round",
                    d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5"
                )
