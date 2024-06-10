import asyncio
from typing import Union

from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.fields import (
    SET_NULL,
    BooleanField,
    CharField,
    ForeignKeyField,
    TextField,
    ForeignKeyNullableRelation,
)
from tortoise.models import Model

from src.models.helpers import GetItemMixin, TimestampMixin, PydanticMixin
from src.models.icon import Icon


class Room(Model, TimestampMixin, GetItemMixin, PydanticMixin):
    name = CharField(max_length=128, unique=True)
    description = TextField(null=True)
    is_favorite = BooleanField(default=False)
    icon: ForeignKeyNullableRelation[Icon] = ForeignKeyField(
        "models.Icon", null=True, on_delete=SET_NULL
    )

    bulbs_state: Union[bool, None] = None
    bulbs_brightness: Union[int, None] = None

    def __str__(self):
        return self.name

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


Room_Py = pydantic_model_creator(Room, name="Room")
