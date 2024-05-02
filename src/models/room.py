import asyncio
from typing import Union, Literal

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
from src.wiz import send_message_to_wiz, MESSAGES, WizMessage, BulbParameters


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
                bulb.wiz_info and bulb.wiz_info.get("state") for bulb in self.bulbs
            )

    async def assign_room_brightness(self) -> None:
        # TODO: should probably be average of all bulbs
        bulb = self.bulbs[0]
        await bulb.assign_wiz_info()
        await asyncio.gather(*[bulb.assign_wiz_info() for bulb in self.bulbs])

        if not any(bulb.wiz_info for bulb in self.bulbs):
            self.bulbs_brightness = None
        if bulb.wiz_info:
            avg = sum(
                int(bulb.wiz_info["dimming"] if bulb.wiz_info["state"] else 0)
                for bulb in self.bulbs
            ) / len(self.bulbs)
            self.bulbs_brightness = int(avg)

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

    async def change_brightness(self, brightness: int) -> None:
        await asyncio.gather(
            *[
                send_message_to_wiz(
                    bulb.ip,
                    message=WizMessage(
                        params=BulbParameters(state=True, brightness=brightness)
                    ),
                )
                for bulb in self.bulbs
            ]
        )

        await self.assign_room_brightness()

    async def set_room_temp_by_name(
        self,
        temp_name: Literal["warmest", "warmer", "warm", "cold", "colder", "coldest"],
    ) -> None:
        await asyncio.gather(
            *[
                send_message_to_wiz(
                    bulb.ip,
                    message=MESSAGES[temp_name.upper()],
                )
                for bulb in self.bulbs
            ]
        )


Room_Py = pydantic_model_creator(Room, name="Room")