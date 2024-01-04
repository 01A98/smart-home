from wtforms import Form, StringField, TextAreaField, validators

from .helpers import get_input_classes, get_styled_label


class RoomForm(Form):
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
