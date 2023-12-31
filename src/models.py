import re
from enum import Enum
from typing import Any, Callable, Coroutine

from tortoise.contrib.pydantic.creator import pydantic_model_creator
from tortoise.exceptions import ValidationError
from tortoise.fields import (
    SET_NULL,
    BooleanField,
    CharEnumField,
    CharField,
    DatetimeField,
    ForeignKeyField,
    ForeignKeyRelation,
    SmallIntField,
    TextField,
)
from tortoise.models import Model
from tortoise.validators import RegexValidator, validate_ipv4_address

from .wiz import ParsedBulbResponse, send_message_to_wiz


def validate_int_in_range(min: int, max: int) -> Callable[[int], None]:
    def _validate_int_in_range(value):
        if not (min <= value <= max):
            raise ValidationError(f"Value must be between {min} and {max}")

    return _validate_int_in_range


class IconVariant(str, Enum):
    DARK = "dark"
    LIGHT = "light"


class TimestampMixin:
    created_at = DatetimeField(null=True, auto_now_add=True)
    updated_at = DatetimeField(null=True, auto_now=True)


class GetItemMixin:
    def __getitem__(self, key: str):
        return getattr(self, key)


class Icon(Model, TimestampMixin, GetItemMixin):
    name = CharField(max_length=128)
    variant = CharEnumField(enum_type=IconVariant, default=IconVariant.LIGHT)
    svg = TextField()

    def __str__(self):
        return self.name


class Setting(Model, TimestampMixin, GetItemMixin):
    name = CharField(max_length=128)
    hex_color = CharField(
        max_length=6,
        comment="Hex color code",
        validators=[RegexValidator(r"^[0-9a-f]{6}$", re.IGNORECASE)],
    )
    color_temperature = SmallIntField(
        comment="Color temperature in Kelvin",
        validators=[validate_int_in_range(2200, 6500)],
    )
    brightness = SmallIntField(
        comment="Brightness in percent",
        validators=[validate_int_in_range(10, 100)],
    )

    def __str__(self):
        return self.name


class Room(Model, TimestampMixin, GetItemMixin):
    name = CharField(max_length=128, unique=True)
    description = TextField(null=True)
    is_favorite = BooleanField(default=False)
    icon: ForeignKeyRelation[Icon] | None = ForeignKeyField(
        "models.Icon", null=True, on_delete=SET_NULL
    )

    def __str__(self):
        return self.name


class Bulb(Model, TimestampMixin, GetItemMixin):
    ip = CharField(validators=[validate_ipv4_address], max_length=15, unique=True)
    name = CharField(max_length=128)
    room: ForeignKeyRelation[Room] | None = ForeignKeyField(
        "models.Room", null=True, on_delete=SET_NULL
    )
    icon: ForeignKeyRelation[Icon] | None = ForeignKeyField(
        "models.Icon", null=True, on_delete=SET_NULL
    )

    def __str__(self) -> str:
        return self.name

    async def assign_wiz_info(self) -> None:
        self.wiz_info = await self.get_wiz_info()

    async def get_wiz_info(self) -> ParsedBulbResponse:
        return await send_message_to_wiz(self.ip)

    async def dict(self) -> dict[str, Any]:
        return (await Bulb_Py.from_tortoise_orm(self)).model_dump()


IconPy = pydantic_model_creator(Icon, name="Icon")
Room_Py = pydantic_model_creator(Room, name="Room")
Bulb_Py = pydantic_model_creator(Bulb, name="Bulb")
Setting_Py = pydantic_model_creator(Setting, name="Setting")
