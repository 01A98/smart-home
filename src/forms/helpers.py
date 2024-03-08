from typing import Union

from markupsafe import Markup
from multidict import MultiDict
from sanic import Request

from models.bulb import Bulb
from models.icon import Icon
from models.room import Room
from models.setting import Setting


def get_input_classes():
    return (
        "shadow-sm bg-gray-50 border border-gray-300 text-gray-900 text-sm "
        "rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 "
        "dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white "
        "dark:focus:ring-blue-500 dark:focus:border-blue-500 dark:shadow-sm-light"
    )


def get_styled_label(text: str, for_: str):
    return Markup(
        f"""
        <label 
            for="{for_}" 
            class="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
        >
            {text}
        </label>
        """
    )


def get_formdata(request: Request):
    formdata = MultiDict()
    if request.form:
        for key, value_list in request.form.items():
            formdata.add(key, value_list[0])
    return formdata


def get_choices(
        records: Union[list[Room], list[Bulb], list[Icon], list[Setting]],
        option_value_field: str = "name",
        is_optional: bool = True,
) -> list[tuple[int, str]]:
    choices = []
    if is_optional:
        choices.append((99999, "Brak"))

    for record in records:
        choices.append((record.pk, record[option_value_field]))

    return choices


def coerce_literal_bool_to_bool(value: str) -> bool:
    if value == "True":
        return True
    elif value == "False":
        return False
    else:
        raise ValueError("Invalid literal for bool() with base 10: '{}'".format(value))


def coerce_rgb_string_to_tuple(value: str) -> tuple[int, int, int]:
    if value.startswith("#"):
        value = value[1:]
    if len(value) != 6:
        raise ValueError("Invalid literal for rgb() with base 10: '{}'".format(value))
    red = int(value[0:2], 16)
    green = int(value[2:4], 16)
    blue = int(value[4:6], 16)
    return red, green, blue


def coerce_wiz_info_to_rgb_string(wiz_info) -> str:
    if not wiz_info:
        return "#ffffff"
    return f"#{wiz_info['r']:02x}{wiz_info['g']:02x}{wiz_info['b']:02x}"
