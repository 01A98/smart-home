import asyncio
from typing import Union, Optional

import wtforms
from tortoise.fields import (
    SET_NULL,
    ForeignKeyNullableRelation,
)
from tortoise.models import Model
from tortoise import fields
from wtforms import validators
from wtforms.form import Form

from src.forms.form_builder import build_form
from src.models.helpers import GetItemMixin, TimestampMixin, PydanticMixin
from src.models.icon import Icon


class Room(Model, TimestampMixin, GetItemMixin, PydanticMixin):
    name = fields.CharField(max_length=128, unique=True)
    description = fields.TextField(null=True)
    is_favorite = fields.BooleanField(default=False)
    icon: ForeignKeyNullableRelation[Icon] = fields.ForeignKeyField(
        "models.Icon", null=True, on_delete=SET_NULL
    )

    bulbs_state: Union[bool, None] = None
    bulbs_brightness: Union[int, None] = None

    def __str__(self):
        return self.name

    @staticmethod
    def get_form(htmx_options: dict[str, str], room: Optional["Room"] = {}):
        room_form = RoomForm(**dict(room))
        return build_form(room_form, htmx_options)

    @classmethod
    def get_room_fields(cls):
        return dict(
            map(lambda field: (field["name"], field), cls.describe()["data_fields"])
        )

    @classmethod
    def get_name_form_validators(cls):
        name_field = cls.get_room_fields()["name"]
        name_validators = []

        if name_field["constraints"]["max_length"]:
            name_validators.append(
                validators.Length(
                    min=1,
                    max=name_field["constraints"]["max_length"],
                    message="Nazwa musi mieć od 1 do 128 znaków",
                )
            )
        if name_field["nullable"] is False:
            name_validators.append(validators.InputRequired())

        return name_validators

    async def assign_room_state(self) -> None:
        await asyncio.gather(*[bulb.assign_wiz_info() for bulb in self.bulbs])

        if not any(bulb.wiz_info for bulb in self.bulbs):
            self.bulbs_state = None
        else:
            self.bulbs_state = any(
                bulb.wiz_info and bulb.wiz_info.state for bulb in self.bulbs
            )

    async def assign_room_brightness(self) -> None:
        await asyncio.gather(*[bulb.assign_wiz_info() for bulb in self.bulbs])

        if not any(bulb.wiz_info for bulb in self.bulbs):
            self.bulbs_brightness = None
        else:
            turned_on_bulbs = list(
                filter(lambda bulb: bulb.wiz_info and bulb.wiz_info.state, self.bulbs)
            )
            # TODO: handle when some are offline
            avg = (
                sum(int(bulb.wiz_info.dimming) for bulb in turned_on_bulbs)
                / len(turned_on_bulbs)
                if len(turned_on_bulbs)
                else 0
            )
            self.bulbs_brightness = int(avg)


class RoomForm(Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    name = wtforms.StringField("Nazwa", Room.get_name_form_validators())
    description = wtforms.TextAreaField("Opis")
