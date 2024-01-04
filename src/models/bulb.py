from tortoise.contrib.pydantic.creator import pydantic_model_creator
from tortoise.fields import SET_NULL, CharField, ForeignKeyField, ForeignKeyRelation
from tortoise.models import Model
from tortoise.validators import validate_ipv4_address

from .helpers import GetItemMixin, TimestampMixin
from .icon import Icon
from .room import Room
from ..wiz import send_message_to_wiz, WizError, WizSetResult, WizGetResult


class Bulb(Model, TimestampMixin, GetItemMixin):
    ip = CharField(validators=[validate_ipv4_address], max_length=15, unique=True)
    name = CharField(max_length=128)
    room: ForeignKeyRelation[Room] | None = ForeignKeyField(
        "models.Room", null=True, on_delete=SET_NULL
    )
    icon: ForeignKeyRelation[Icon] | None = ForeignKeyField(
        "models.Icon", null=True, on_delete=SET_NULL
    )

    wiz_info: str | WizError | WizSetResult | WizGetResult | None = None

    def __str__(self) -> str:
        return self.name

    async def assign_wiz_info(self) -> None:
        error, result = await send_message_to_wiz(self.ip)
        self.wiz_info = error if error else result.model_dump()


Bulb_Py = pydantic_model_creator(Bulb, name="Bulb")
