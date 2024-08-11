from typing import Optional

import wtforms
from tortoise import fields
from tortoise.fields import (
    SET_NULL,
    ForeignKeyField,
    ForeignKeyNullableRelation,
)
from tortoise.models import Model
from tortoise.validators import validate_ipv4_address
from wtforms import validators
from wtforms.form import Form

from src.forms.form_builder import build_form
from src.forms.helpers import get_choices
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
    ip = fields.CharField(
        validators=[validate_ipv4_address], max_length=15, unique=True
    )
    name = fields.CharField(max_length=128)
    room: ForeignKeyNullableRelation[Room] = ForeignKeyField(
        "models.Room", null=True, on_delete=SET_NULL, related_name="bulbs"
    )
    icon: ForeignKeyNullableRelation[Icon] = ForeignKeyField(
        "models.Icon", null=True, on_delete=SET_NULL
    )

    wiz_info: WizGetResult = {}

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def get_form(
        htmx_options: dict[str, str], rooms: list[Room], bulb: Optional["Bulb"] = {}
    ):
        bulb_form = BulbForm(**dict(bulb))
        choices = get_choices(rooms, "name")
        bulb_form.room_id.choices = choices

        return build_form(bulb_form, htmx_options)

    # TODO: use mixin?
    @classmethod
    def get_bulb_fields(cls):
        return dict(
            map(lambda field: (field["name"], field), cls.describe()["data_fields"])
        )

    @classmethod
    def get_name_form_validators(cls):
        name_field = cls.get_bulb_fields()["name"]
        name_validators = []

        if name_field["constraints"]["max_length"]:
            name_validators.append(
                validators.Length(
                    min=1,
                    max=name_field["constraints"]["max_length"],
                    message="Nazwa musi mieć od 1 do 128 znaków",
                )
            )
        if name_field["nullable"] is False:
            name_validators.append(validators.InputRequired())

        return name_validators

    @classmethod
    def get_ip_address_validators(cls):
        ip_address_field = cls.get_bulb_fields()["ip"]
        ip_address_validators = [wtforms.validators.IPAddress()]

        if ip_address_field["constraints"]["max_length"]:
            ip_address_validators.append(
                validators.Length(
                    min=1,
                    max=ip_address_field["constraints"]["max_length"],
                    message="Adres IP może mieć maksymalnie 15 znaków (w tym 4 kropki)",
                )
            )
        if ip_address_field["nullable"] is False:
            ip_address_validators.append(validators.InputRequired())

        return ip_address_validators

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


class BulbForm(Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    name = wtforms.StringField("Nazwa", Bulb.get_name_form_validators())
    # TODO: ip should be unique, figure out async validators or use htmx
    ip = wtforms.StringField("Adres IP żarówki", Bulb.get_ip_address_validators())
    room_id = wtforms.SelectField(
        "Pokój",
        [wtforms.validators.Optional()],
        coerce=str,
        default="",
        # render_kw={"autocomplete": "off"},
    )
