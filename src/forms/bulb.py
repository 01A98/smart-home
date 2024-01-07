import re
from decimal import Decimal

import wtforms
from sanic import Sanic

from .helpers import get_input_classes, get_styled_label
from ..models.bulb import Bulb


class BulbDetailsForm(wtforms.Form):
    name = wtforms.StringField(
        get_styled_label("Nazwa", "name"),
        [
            wtforms.validators.Length(
                min=1, max=128, message="Nazwa musi mieć od 1 do 128 znaków"
            ),
            wtforms.validators.InputRequired(),
        ],
        render_kw={"class": get_input_classes()},
    )
    ip_address = wtforms.StringField(
        get_styled_label("Adres IP", "ip_address"),
        [
            wtforms.validators.Regexp(
                re.compile(
                    r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$",
                ),
                message="Niepoprawny adres IP",
            ),
            wtforms.validators.InputRequired(),
        ],
        render_kw={"placeholder": "XXX.XXX.XXX.XXX", "class": get_input_classes()},
    )
    room = wtforms.SelectField(
        get_styled_label("Pokój", "room"),
        [wtforms.validators.Optional()],
        coerce=str,
        default="",
        render_kw={"class": get_input_classes()},
    )


def bulb_control_form_factory(bulb: Bulb, app: Sanic):
    bulb_state_value = None
    if bulb.wiz_info:
        if bulb.wiz_info["state"] is False:
            bulb_state_value = "n"
        elif bulb.wiz_info["state"] is True:
            bulb_state_value = "y"

    class BulbControlForm(wtforms.Form):
        state = wtforms.BooleanField(
            get_styled_label("Włączona", "state"),
            render_kw={
                "toggle": "true",
                "class": "scale-[1.5] origin-left pt-2",
                "hx-post": app.url_for("bulb_control", id=bulb.id),
                "hx-target": "#bulb-details-form",
                "hx-swap": "innerHTML",
            },
            **({"default": "y"} if bulb_state_value == "y" else {}),
        )
        state_value = wtforms.HiddenField(
            validators=[
                wtforms.validators.InputRequired(),
            ],
            default="n"
            if bulb_state_value == "y"
            else "y",  # reverse bc it's a reference field for state
        )
        color = wtforms.ColorField(
            get_styled_label("Kolor", "color"),
            [
                wtforms.validators.Regexp(
                    re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$"),
                    message="Niepoprawny kolor",
                ),
                wtforms.validators.InputRequired(),
            ],
            render_kw={
                "hx-post": app.url_for("bulb_control", id=bulb.id),
                "hx-target": "#bulb-details-form",
                "hx-swap": "innerHTML",
                "class": "p-2 h-10 w-14 block bg-white border "
                "scale-[1.25] "
                "border-gray-200 cursor-pointer w-10 rounded-lg "
                "disabled:opacity-50 disabled:pointer-events-none "
                "dark:bg-slate-900 dark:border-gray-700",
            },
        )
        brightness = wtforms.DecimalRangeField(
            get_styled_label("Jasność", "brightness"),
            [
                wtforms.validators.NumberRange(
                    min=10,
                    max=100,
                    message="Zakres jasności od 10 do 100 (z krokiem 10)",
                ),
            ],
            default=Decimal(bulb.wiz_info["dimming"] if bulb.wiz_info else 100),
            render_kw={
                "hx-post": app.url_for("bulb_control", id=bulb.id),
                "hx-target": "#bulb-details-form",
                "hx-swap": "innerHTML",
                "step": 10,
                "list": "brightness-list",
                "class": "accent-blue-500 origin-left scale-[2.0] w-1/2",
            },
        )
        temperature = wtforms.DecimalRangeField(
            get_styled_label("Temperatura", "temperature"),
            [
                wtforms.validators.NumberRange(
                    min=2200,
                    max=6500,
                    message="Zakres temperatury od 2200 do 6500",
                ),
            ],
            default=Decimal(bulb.wiz_info["temp"] if bulb.wiz_info else 4250),
            render_kw={
                "hx-post": app.url_for("bulb_control", id=bulb.id),
                "hx-target": "#bulb-details-form",
                "hx-swap": "innerHTML",
                "list": "temperature-list",
                "class": "accent-blue-500 origin-left scale-[2.0] w-1/2",
            },
        )

    return BulbControlForm
