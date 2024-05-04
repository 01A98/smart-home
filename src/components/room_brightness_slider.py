from dominate.tags import button, div, label, span
from dominate.util import raw
from sanic import Sanic

from src.components.spinner import Spinner
from src.models.room import Room


class RoomBrightnessSlider(button):
    tagname = "div"
    id = "app-brightness-slider"
    route = "room_bulbs_brightness"
    app: Sanic
    room: Room

    def __init__(self, app: Sanic, room: Room = None) -> None:
        super().__init__()
        self.app = app
        self.room = room

        with self:
            if room.bulbs_brightness is None:
                (span("Brak podłączonych żarówek w pokoju", class_name="sr-only"),)
            else:
                label(
                    span("Ustaw jasność", class_name="sr-only"),
                    html_for="group_brightness",
                )
                self._brightness_slider_input()

    @classmethod
    def lazy_load(cls, app: Sanic, room: Room) -> div:
        return div(
            Spinner(htmx_indicator=True),
            class_name="w-full",
            **{
                "hx-get": app.url_for(cls.route, id=room.id),
                "hx-trigger": f"load, change-bulb-state from:#room-{room.id}, change-room-state from:#room-{room.id}",
                "hx-swap": "innerHTML",
            },
        )

    def _brightness_slider_input(self) -> raw:
        return raw(
            f"""
                <input 
                    name="group_brightness" 
                    id="group_brightness" 
                    type="range"
                    value="{self.room.bulbs_brightness}"
                    class="accent-blue-500 origin-left scale-[2.0] w-1/2"
                    min="0"
                    max="100"
                    step="10"
                    hx-post="{self.app.url_for("room-brigthness", id=self.room.id)}"
                />
            """
            #     hx-post="{self.app.url_for("change_room_brightness", id=self.room.id)}"
        )
