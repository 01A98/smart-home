import asyncio
from typing import Union

from tortoise.contrib.pydantic.creator import pydantic_model_creator
from tortoise.fields import (
    SET_NULL,
    BooleanField,
    CharField,
    ForeignKeyField,
    ForeignKeyRelation,
    TextField,
)
from tortoise.models import Model

from wiz import send_message_to_wiz, MESSAGES
from .helpers import GetItemMixin, TimestampMixin
from .icon import Icon


class Room(Model, TimestampMixin, GetItemMixin):
    name = CharField(max_length=128, unique=True)
    description = TextField(null=True)
    is_favorite = BooleanField(default=False)
    icon: Union[ForeignKeyRelation[Icon], None] = ForeignKeyField(
        "models.Icon", null=True, on_delete=SET_NULL
    )

    bulbs_state: bool = None

    def __str__(self):
        return self.name

    async def assign_room_state(self) -> None:
        await asyncio.gather(*[bulb.assign_wiz_info() for bulb in self.bulbs])
        self.bulbs_state = any(bulb.wiz_info["state"] for bulb in self.bulbs)

    async def toggle_state(self, state: bool) -> None:
        await asyncio.gather(
            *[
                send_message_to_wiz(
                    bulb.ip, message=MESSAGES["ON"] if state else MESSAGES["OFF"]
                )
                for bulb in self.bulbs
            ]
        )

        await self.assign_room_state()


Room_Py = pydantic_model_creator(Room, name="Room")
