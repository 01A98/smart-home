from enum import Enum

from tortoise.contrib.pydantic.creator import pydantic_model_creator
from tortoise.fields import CharEnumField, CharField, TextField
from tortoise.models import Model

from .helpers import GetItemMixin, TimestampMixin


class IconVariant(str, Enum):
    DARK = "dark"
    LIGHT = "light"


class Icon(Model, TimestampMixin, GetItemMixin):
    name = CharField(max_length=128)
    variant = CharEnumField(enum_type=IconVariant, default=IconVariant.LIGHT)
    svg = TextField()

    def __str__(self):
        return self.name


IconPy = pydantic_model_creator(Icon, name="Icon")
