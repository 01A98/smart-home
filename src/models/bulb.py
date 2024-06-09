from tortoise.contrib.pydantic.creator import pydantic_model_creator
from tortoise.fields import (
    SET_NULL,
    CharField,
    ForeignKeyField,
    ForeignKeyNullableRelation,
)
from tortoise.models import Model
from tortoise.validators import validate_ipv4_address

from src.models.helpers import GetItemMixin, TimestampMixin
from src.models.icon import Icon
from src.models.room import Room
from src.wiz import (
    send_message_to_wiz,
    MESSAGES,
    WizMessage,
    BulbParameters,
    WizGetResult,
)


class Bulb(Model, TimestampMixin, GetItemMixin):
    ip = CharField(validators=[validate_ipv4_address], max_length=15, unique=True)
    name = CharField(max_length=128)
    room: ForeignKeyNullableRelation[Room] = ForeignKeyField(
        "models.Room", null=True, on_delete=SET_NULL
    )
    icon: ForeignKeyNullableRelation[Icon] = ForeignKeyField(
        "models.Icon", null=True, on_delete=SET_NULL
    )

    wiz_info: WizGetResult = {}

    def __str__(self) -> str:
        return self.name

    async def assign_wiz_info(self) -> None:
        error, result = await send_message_to_wiz(self.ip, MESSAGES["INFO"])
        self.wiz_info = {} if error else result

    async def toggle_state(self, state: bool) -> None:
        error, res = await send_message_to_wiz(
            self.ip, message=MESSAGES["ON"] if state else MESSAGES["OFF"]
        )
        await self.assign_wiz_info()

    async def set_brightness(self, brightness: int) -> bool:
        message = (
            WizMessage(params=BulbParameters(state=True, brightness=brightness))
            if brightness > 0
            else MESSAGES["OFF"]
        )
        error, res = await send_message_to_wiz(
            self.ip,
            message,
        )
        await self.assign_wiz_info()

    async def send_message(self, message: WizMessage) -> None:
        error, res = await send_message_to_wiz(self.ip, message=message)
        await self.assign_wiz_info()


Bulb_Py = pydantic_model_creator(Bulb, name="Bulb")
