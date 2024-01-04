from typing import Callable

from tortoise.exceptions import ValidationError
from tortoise.fields import DatetimeField


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
