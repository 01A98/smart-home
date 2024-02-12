from dominate.svg import svg, path
from dominate.tags import html_tag

from ..models.bulb import Bulb


class bulb_icon(html_tag):
    tagname = "app-bulb-icon"

    def __init__(self, bulb: Bulb = None) -> None:
        super().__init__()

        self._is_offline = bulb.wiz_info is None or bulb.wiz_info == "Bulb offline"
        self._is_on = bulb.wiz_info["state"] if not self._is_offline else False

        with self:
            if self._is_offline:
                svg(
                    path(
                        d="M288 32c0-17.7-14.3-32-32-32s-32 14.3-32 32V256c0 17.7 14.3 32 32 32s32-14.3 "
                        "32-32V32zM143.5 "
                        "120.6c13.6-11.3 15.4-31.5 4.1-45.1s-31.5-15.4-45.1-4.1C49.7 115.4 16 181.8 16 256c0 132.5 "
                        "107.5 240 240 240s240-107.5 240-240c0-74.2-33.8-140.6-86.6-184.6c-13.6-11.3-33.8-9.4-45.1 "
                        "4.1s-9.4 33.8 4.1 45.1c38.9 32.3 63.5 81 63.5 135.4c0 97.2-78.8 176-176 "
                        "176s-176-78.8-176-176c0-54.4 "
                        "24.7-103.1 63.5-135.4z",
                    ),
                    xmlns="http://www.w3.org/2000/svg",
                    class_name="w-8 h-6 fill-gray-400",
                    viewBox="0 0 384 512",
                )
            else:
                svg(
                    path(
                        d="M272 384c9.6-31.9 29.5-59.1 49.2-86.2l0 0c5.2-7.1 10.4-14.2 15.4-21.4c19.8-28.5 31.4-63 "
                        "31.4-100.3C368 78.8 289.2 0 192 0S16 78.8 16 176c0 37.3 11.6 71.9 31.4 100.3c5 7.2 10.2 14.3 "
                        "15.4 "
                        "21.4l0 0c19.8 27.1 39.7 54.4 49.2 86.2H272zM192 512c44.2 0 80-35.8 80-80V416H112v16c0 44.2 "
                        "35.8 80 "
                        "80 80zM112 176c0 8.8-7.2 16-16 16s-16-7.2-16-16c0-61.9 50.1-112 112-112c8.8 0 16 7.2 16 "
                        "16s-7.2 "
                        "16-16 16c-44.2 0-80 35.8-80 80z",
                    ),
                    xmlns="http://www.w3.org/2000/svg",
                    class_name=f"w-6 h-6 fill-{'yellow-400' if self._is_on else 'gray-400'}",
                    viewBox="0 0 384 512",
                )
