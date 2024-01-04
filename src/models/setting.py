import re

from tortoise.contrib.pydantic.creator import pydantic_model_creator
from tortoise.fields import CharField, SmallIntField
from tortoise.models import Model
from tortoise.validators import RegexValidator

from .helpers import GetItemMixin, TimestampMixin, validate_int_in_range


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


Setting_Py = pydantic_model_creator(Setting, name="Setting")
