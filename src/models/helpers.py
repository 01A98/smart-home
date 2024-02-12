from __future__ import annotations

from typing import Callable, TYPE_CHECKING

from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import ValidationError
from tortoise.fields import DatetimeField

if TYPE_CHECKING:
    from pydantic import BaseModel as PydanticModel
    from tortoise.models import Model


def validate_int_in_range(min: int, max: int) -> Callable[[int], None]:
    def _validate_int_in_range(value):
        if not (min <= value <= max):
            raise ValidationError(f"Value must be between {min} and {max}")

    return _validate_int_in_range


class TimestampMixin:
    created_at = DatetimeField(null=True, auto_now_add=True)
    updated_at = DatetimeField(null=True, auto_now=True)


class GetItemMixin:
    def __getitem__(self, key: str):
        return getattr(self, key)


class PydanticMixin:
    @classmethod
    async def get_all(cls: type[Model]) -> list[PydanticModel]:
        Model_Py = pydantic_model_creator(cls, name=cls.__name__)
        return await Model_Py.from_queryset(cls.all())

    @classmethod
    async def get_one(cls: type[Model]) -> PydanticModel:
        Model_Py = pydantic_model_creator(cls, name=cls.__name__)
        return await Model_Py.from_queryset_single(cls.get())
