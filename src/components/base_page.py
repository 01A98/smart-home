from __future__ import annotations

from typing import TYPE_CHECKING

from dominate import document
from dominate.tags import meta, link, style, script
from dominate.util import raw

if TYPE_CHECKING:
    from dominate.tags import html_tag


class BasePage(document):
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
            self.add_scripts()
            self.add_stylesheets()

        self.body["hx-boost"] = "true"
        self.body["hx-ext"] = "head-support"

        self.add(*args)

    @staticmethod
    def add_stylesheets() -> None:
        # Material Tailwind
        link(
            href="https://unpkg.com/@material-tailwind/html@latest/styles/material-tailwind.css",
            rel="stylesheet",
        )

        # Material Icons
        link(
            href="https://fonts.googleapis.com/icon?family=Material+Icons+Round",
            rel="stylesheet",
        )
        link(
            href="https://fonts.googleapis.com/icon?family=Material+Symbols+Rounded",
            rel="stylesheet",
        )

        # Web Font
        link(
            href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap",
            rel="stylesheet",
        )

        # HTMX
        style(
            raw(
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
            )
        )

    @staticmethod
    def add_scripts() -> None:
        # Material Tailwind
        script(src="https://cdn.tailwindcss.com")
        script(
            raw("""
                tailwind.config = { 
                  theme: {
                    fontFamily: { 
                      sans: ['Montserrat'],
                      serif: ['Montserrat'],
                      mono: ['Montserrat'],
                      display: ['Montserrat'],
                      body: ['Montserrat']
                    }
                  }
                }
                """),
            type="text/javascript",
        )
        script(
            src="https://unpkg.com/@material-tailwind/html@latest/scripts/ripple.js",
            defer=True,
            **{
                "hx-head": "re-eval"
            }
        )
        script(
            src="https://unpkg.com/@material-tailwind/html@latest/scripts/collapse.js",
            defer=True,
            **{
                "hx-head": "re-eval"
            }
        )

        # AlpineJS
        # script(src="//unpkg.com/alpinejs", defer=True)

        # HTMX
        script(src="https://unpkg.com/htmx.org@1.9.10")
        script(src="https://unpkg.com/htmx.org/dist/ext/head-support.js")
        script("htmx.config.globalViewTransitions = true;", type="text/javascript")
