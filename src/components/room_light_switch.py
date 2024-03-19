from dominate.tags import button, div, input_, label, span
from sanic import Sanic

from src.components.spinner import Spinner
from src.models.room import Room


class RoomLightSwitch(button):
    tagname = "form"
    id = "app-light-switch"
    route = "room_bulbs_state"

    def __init__(self, app: Sanic, room: Room = None) -> None:
        super().__init__()

        with self:
            reference_input_value = "true" if room.bulbs_state else "false"

            if room.bulbs_state is None:
                (span("Brak podłączonych żarówek w pokoju", class_name="sr-only"),)
            else:
                input_(
                    type="hidden", name="room_state_value", value=reference_input_value
                )
                label(
                    span("Włącz lub wyłącz wszystkie zarówki", class_name="sr-only"),
                    html_for="room_state",
                    class_name="flex items-center",
                )
                input_(
                    name="room_state",
                    id="room_state",
                    type="checkbox",
                    toggle=True,
                    **{"checked": room.bulbs_state} if room.bulbs_state is True else {},
                    **{
                        "hx-post": app.url_for("toggle_room_state", id=room.id),
                        "hx-swap": "outerHTML",
                    },
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
