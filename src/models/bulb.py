from tortoise.contrib.pydantic.creator import pydantic_model_creator
from tortoise.fields import SET_NULL, CharField, ForeignKeyField, ForeignKeyRelation
from tortoise.models import Model
from tortoise.validators import validate_ipv4_address

from .helpers import GetItemMixin, TimestampMixin
from .icon import Icon
from .room import Room
from ..wiz import send_message_to_wiz, MESSAGES, WizMessage


class Bulb(Model, TimestampMixin, GetItemMixin):
    ip = CharField(validators=[validate_ipv4_address], max_length=15, unique=True)
    name = CharField(max_length=128)
    room: [ForeignKeyRelation[Room], None] = ForeignKeyField(
        "models.Room", null=True, on_delete=SET_NULL
    )
    icon: [ForeignKeyRelation[Icon], None] = ForeignKeyField(
        "models.Icon", null=True, on_delete=SET_NULL
    )

    wiz_info = None

    def __str__(self) -> str:
        return self.name

    async def assign_wiz_info(self) -> None:
        error, result = await send_message_to_wiz(self.ip)
        self.wiz_info = error if error else result.model_dump()

    async def toggle_state(self, state: bool) -> None:
        error, res = await send_message_to_wiz(
            self.ip, message=MESSAGES["ON"] if state else MESSAGES["OFF"]
        )
        await self.assign_wiz_info()

    async def send_message(self, message: WizMessage) -> None:
        error, res = await send_message_to_wiz(self.ip, message=message)
        await self.assign_wiz_info()


Bulb_Py = pydantic_model_creator(Bulb, name="Bulb")
