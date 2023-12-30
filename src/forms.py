import re

from markupsafe import Markup
from multidict import MultiDict
from sanic import Request
from wtforms import Form, StringField, validators, TextAreaField

from .form_helpers import get_styled_label, get_input_classes


class BulbForm(Form):
    name = StringField(
        get_styled_label("Nazwa", "name"),
        [
            validators.Length(
                min=1, max=128, message="Nazwa musi mieć od 1 do 128 znaków"
            ),
            validators.InputRequired(),
        ],
        render_kw={"placeholder": "Lampka", "class": get_input_classes()},
    )
    ip_address = StringField(
        get_styled_label("Adres IP", "ip_address"),
        [
            validators.Regexp(
                re.compile(
                    r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$",
                ),
                message="Niepoprawny adres IP",
            ),
            validators.InputRequired(),
        ],
        render_kw={"placeholder": "XXX.XXX.XXX.XXX", "class": get_input_classes()},
    )


class RoomForm(Form):
    name = StringField(
        get_styled_label("Nazwa", "name"),
        [
            validators.Length(
                min=1, max=128, message="Nazwa musi mieć od 1 do 128 znaków"
            ),
            validators.InputRequired(),
        ],
        render_kw={"placeholder": "Salon", "class": get_input_classes()},
    )
    description = TextAreaField(
        get_styled_label("Opis", "description"),
        [
            validators.Optional(),
            validators.Length(
                min=1, max=128, message="Opis musi mieć od 1 do 128 znaków"
            ),
        ],
        render_kw={"placeholder": "...", "class": get_input_classes()},
    )
