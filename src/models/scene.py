from typing import Union

from tortoise.fields import (
    CharField,
    IntField,
    ForeignKeyRelation,
    ForeignKeyField,
    SET_NULL,
)
from tortoise.models import Model

from .helpers import GetItemMixin, TimestampMixin
from .icon import Icon


class Scene(Model, TimestampMixin, GetItemMixin):
    sceneId = IntField(pk=True)
    name = CharField(max_length=128)
    icon: Union[ForeignKeyRelation[Icon], None] = ForeignKeyField(
        "models.Icon", null=True, on_delete=SET_NULL
    )

    def __str__(self):
        return self.name
