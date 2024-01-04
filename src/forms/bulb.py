import re

from wtforms import Form, SelectField, StringField, validators

from .helpers import get_input_classes, get_styled_label


class BulbForm(Form):
    name = StringField(
        get_styled_label("Nazwa", "name"),
        [
            validators.Length(
                min=1, max=128, message="Nazwa musi mieć od 1 do 128 znaków"
            ),
            validators.InputRequired(),
        ],
        render_kw={"class": get_input_classes()},
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
    room = SelectField(
        get_styled_label("Pokój", "room"),
        [validators.Optional()],
        coerce=str,
        default="",
        render_kw={"class": get_input_classes()},
    )
