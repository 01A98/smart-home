from __future__ import annotations

from typing import TYPE_CHECKING

from dominate import document
from dominate.tags import meta, link, style, script

if TYPE_CHECKING:
    from dominate.tags import html_tag


class base_page(document):
    def __init__(self, *args: html_tag, title: str = "Smart Home") -> None:
        super().__init__(title=title)

        with self.head:
            meta(charset="utf-8")
            meta(name="viewport", content="width=device-width, initial-scale=1.0")
            link(
                rel="icon",
                href="/assets/bolt.svg",
                type="image/svg",
            )
            self.add_stylesheets()
            self.add_scripts()

        self.add(*args)

    @staticmethod
    def add_stylesheets() -> None:
        # Flowbite css
        link(
            href="https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.1.1/flowbite.min.css",
            rel="stylesheet",
        )
        with style():
            """
                /* HTMX */
                .htmx-indicator {
                    opacity: 0;
                    transition: opacity 300ms ease-in;
                }
        
                .htmx-request .htmx-indicator {
                    opacity: 1
                }
        
                .htmx-request.htmx-indicator {
                    opacity: 1
                }
        
                /* AlpineJS */
                [x-cloak] {
                    display: none !important;
                }
        
                /* Toggle input */
                input[toggle] {
                    appearance: none;
                    position: relative;
                    display: inline-block;
                    background: lightgrey;
                    height: 1.65rem;
                    width: 2.75rem;
                    vertical-align: middle;
                    border-radius: 2rem;
                    box-shadow: 0 1px 3px #0003 inset;
                    transition: 0.25s linear background;
                }
        
                input[toggle]::before {
                    content: "";
                    display: block;
                    width: 1.25rem;
                    height: 1.25rem;
                    background: #fff;
                    border-radius: 1.2rem;
                    position: absolute;
                    top: 0.2rem;
                    left: 0.2rem;
                    box-shadow: 0 1px 3px #0003;
                    transition: 0.25s linear transform;
                    transform: translateX(0rem);
                }
        
                input[toggle]:checked {
                    background: #05c905;
                }
        
                input[toggle]:checked::before {
                    transform: translateX(1rem);
                }
            """

    @staticmethod
    def add_scripts() -> None:
        script(src="https://cdn.tailwindcss.com")
        script(
            src="https://cdnjs.cloudflare.com/ajax/libs/flowbite/2.1.1/flowbite.min.js",
            defer="",
        )
        script(src="//unpkg.com/alpinejs", defer="")
        script(src="https://unpkg.com/htmx.org@1.9.10")
        script(src="https://unpkg.com/htmx.org/dist/ext/head-support.js")
        script("htmx.config.globalViewTransitions = true;", type="text/javascript")
