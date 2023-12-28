from enum import Enum

from tortoise.contrib.pydantic.creator import pydantic_model_creator
from tortoise.fields import (
    SET_NULL,
    BooleanField,
    CharEnumField,
    CharField,
    DatetimeField,
    ForeignKeyField,
    ForeignKeyRelation,
    TextField,
)
from tortoise.models import Model
from tortoise.validators import validate_ipv4_address


class IconVariant(str, Enum):
    DARK = "dark"
    LIGHT = "light"


class TimestampMixin:
    created_at = DatetimeField(null=True, auto_now_add=True)
    updated_at = DatetimeField(null=True, auto_now=True)


class Icon(Model, TimestampMixin):
    name = CharField(max_length=128)
    variant = CharEnumField(enum_type=IconVariant, default=IconVariant.LIGHT)
    svg = TextField()

    def __str__(self):
        return self.name


class Room(Model, TimestampMixin):
    name = CharField(max_length=128, unique=True)
    description = TextField(null=True)
    is_favorite = BooleanField(default=False)
    icon: ForeignKeyRelation[Icon] | None = ForeignKeyField(
        "models.Icon", null=True, on_delete=SET_NULL
    )

    def __str__(self):
        return self.name


class Bulb(Model, TimestampMixin):
    ip = TextField(validators=[validate_ipv4_address])
    name = CharField(max_length=128)
    room: ForeignKeyRelation[Room] | None = ForeignKeyField(
        "models.Room", null=True, on_delete=SET_NULL
    )
    icon: ForeignKeyRelation[Icon] | None = ForeignKeyField(
        "models.Icon", null=True, on_delete=SET_NULL
    )

    def __str__(self):
        return self.name


Room_Py = pydantic_model_creator(Room, name="Room")
Bulb_Py = pydantic_model_creator(Bulb, name="Bulb")
