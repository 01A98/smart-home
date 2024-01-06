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

from .helpers import GetItemMixin, TimestampMixin
from .icon import Icon


class Room(Model, TimestampMixin, GetItemMixin):
    name = CharField(max_length=128, unique=True)
    description = TextField(null=True)
    is_favorite = BooleanField(default=False)
    icon: Union[ForeignKeyRelation[Icon], None] = ForeignKeyField(
        "models.Icon", null=True, on_delete=SET_NULL
    )

    def __str__(self):
        return self.name


Room_Py = pydantic_model_creator(Room, name="Room")
