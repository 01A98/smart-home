from typing import Literal

from dominate.tags import html_tag, div, button
from sanic import Sanic

from ..models.room import Room


class RoomTemperatureButtonGroup(html_tag):
    room: Room
    app: Sanic
    tagname = "app-room-temperature-button-group"

    def __init__(self, room: Room, app: Sanic) -> None:
        super().__init__()
        self.room = room
        self.app = app

        with self:
            with div(
                    id=f"room-{self.room.id}-temperature-button-group",
                    class_name=(
                            "flex flex-col justify-center items-center gap-y-3 p-4 rounded-lg "
                            "hover:border-gray-400 border-gray-200 border"
                    ),
            ):
                with div(class_name="flex flex-row justify-center gap-x-3"):
                    self.temp_control_button("warmest", "bg-red-400 hover:bg-red-500")
                    self.temp_control_button(
                        "warmer", "bg-orange-400 hover:bg-orange-500"
                    )
                    self.temp_control_button(
                        "warm", "bg-yellow-400 hover:bg-yellow-500"
                    )
                with div(class_name="flex flex-row justify-center gap-x-3"):
                    self.temp_control_button("cold", "bg-white hover:bg-cyan-100")
                    self.temp_control_button("colder", "bg-cyan-200 hover:bg-cyan-300")
                    self.temp_control_button("coldest", "bg-cyan-400 hover:bg-cyan-500")

    def temp_control_button(
            self,
            temp_name: Literal["warmest", "warmer", "warm", "cold", "colder", "coldest"],
            color_classes: str,
    ) -> button:
        return button(
            type="button",
            id=f"room-{self.room.id}-bulbs-{temp_name}",
            class_name=f"{color_classes} focus:ring-4 rounded-full p-5",
            **{
                "hx-swap": "none",
                "hx-post": f"{self.app.url_for('room_bulbs_temp_name', id=self.room.id, temp_name=temp_name)}",
            },
        )
