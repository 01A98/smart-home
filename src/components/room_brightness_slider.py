from dominate.tags import button, div, label, span
from dominate.util import raw
from sanic import Sanic

from src.components.spinner import Spinner
from src.models.room import Room


class RoomBrightnessSlider(button):
    tagname = "form"
    id = "app-brightness-slider"
    route = "room_bulbs_brightness"

    def __init__(self, app: Sanic, room: Room = None) -> None:
        super().__init__()

        with self:
            if room.bulbs_brightness is None:
                (span("Brak podłączonych żarówek w pokoju", class_name="sr-only"),)
            else:
                label(
                    span("Ustaw jasność", class_name="sr-only"),
                    html_for="group_brightness",
                )
                # input_ tag doesn't work with value attribute correctly
                raw(
                    f"""
                    <input name="group_brightness" id="group_brightness" type="range"
                           value="{room.bulbs_brightness}"
                           class="accent-blue-500 origin-left scale-[1.8] w-4/5"
                           hx-post="{app.url_for("change_room_brightness", id=room.id)}"
                           hx-target="#room-{room.id}-brightness-form"
                           hx-swap="outerHTML"
                           hx-trigger="change, reloadRoom{room.id}BulbsBrightness from:body"
                           min="10"
                           max="100"
                    />
                    """
                )

    @classmethod
    def lazy_load(cls, app: Sanic, room: Room) -> div:
        return div(
            Spinner(htmx_indicator=True),
            **{
                "hx-get": app.url_for(cls.route, id=room.id),
                "hx-trigger": "load",
                "hx-swap": "outerHTML",
            },
        )
