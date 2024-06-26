from typing import Optional

from dominate.svg import svg, path
from dominate.tags import html_tag, span, input_


class Checkbox(html_tag):
    tagname = "label"

    def __init__(self, name="checkbox", id_="checkbox", event: Optional[tuple[str, str]] = None, **kwargs) -> None:
        super().__init__(**kwargs)

        self["for"] = id_
        self["class"] = "relative -ml-2.5 flex cursor-pointer items-center rounded-full p-3"

        with self:
            input_(
                type="checkbox",
                checkbox="true",
                id=id_,
                name=name,
                class_name="before:content[''] peer relative h-5 w-5 cursor-pointer appearance-none "
                           "rounded-md border border-blue-gray-200 transition-all before:absolute "
                           "before:top-2/4 before:left-2/4 before:block before:h-12 before:w-12 "
                           "before:-translate-y-2/4 before:-translate-x-2/4 before:rounded-full "
                           "before:bg-blue-gray-500 before:opacity-0 before:transition-opacity "
                           "checked:border-gray-900 checked:bg-gray-900 checked:before:bg-gray-900 "
                           "hover:before:opacity-10",
                **{f"@{event[0]}": event[1]} if event else {}
            )
            with span(
                    class_name="absolute text-white transition-opacity opacity-0 pointer-events-none top-2/4 "
                               "left-2/4 -translate-y-2/4 -translate-x-2/4 peer-checked:opacity-100"
            ):
                with svg(
                        xmlns="http://www.w3.org/2000/svg",
                        class_name="h-3.5 w-3.5",
                        viewBox="0 0 20 20",
                        fill="currentColor",
                        stroke="currentColor",
                        stroke_width="1"
                ):
                    path(
                        fill_rule="evenodd",
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 "
                          "12.586l7.293-7.293a1 1 0 011.414 0z",
                        clip_rule="evenodd",
                    )
