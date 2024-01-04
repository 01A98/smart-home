from markupsafe import Markup
from multidict import MultiDict
from sanic import Request

from ..models.bulb import Bulb
from ..models.icon import Icon
from ..models.room import Room
from ..models.setting import Setting


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
    records: list[Room] | list[Bulb] | list[Icon] | list[Setting],
    option_value_field: str = "name",
    is_optional: bool = True,
) -> list[tuple[int, str]]:
    choices = []
    if is_optional:
        choices.append((99999, "Brak"))

    for record in records:
        choices.append((record.pk, record[option_value_field]))

    return choices