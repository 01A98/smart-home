from dominate.tags import button, div, form
from dominate.util import raw
from wtforms.form import Form


def build_form(
    wtform: Form,
    htmx_options: dict[str, str] = {},
    with_submit_button: bool = True,
) -> form:
    with form(
        class_name="flex flex-col items-center w-full h-full py-6",
        **htmx_options,
        #     TODO: add indicator
    ) as form_:
        with div(
            class_name="flex flex-col items-center lg:w-1/2 md:w-2/3 w-3/4 gap-y-6 rounded-md p-4"
        ):
            for field in wtform:
                if field.type == "StringField":
                    with div(
                        class_name="relative w-full min-w-[200px] h-10",
                    ):
                        raw(
                            field(
                                placeholder=" ",
                                class_="peer w-full h-full bg-transparent text-blue-gray-700 font-sans font-normal "
                                "outline outline-0 focus:outline-0 disabled:bg-blue-gray-50 disabled:border-0 "
                                "transition-all placeholder-shown:border placeholder-shown:border-gray-200 "
                                "placeholder-shown:border-t-gray-200 border focus:border-2 "
                                "border-t-transparent focus:border-t-transparent text-sm px-3 py-2.5 rounded-[7px] "
                                "border-gray-200 focus:border-gray-900",
                            )
                        )
                        raw(
                            field.label(
                                class_="flex w-full h-full select-none pointer-events-none absolute left-0 font-normal "
                                "!overflow-visible truncate peer-placeholder-shown:text-blue-gray-500 "
                                "leading-tight peer-focus:leading-tight peer-disabled:text-transparent "
                                "peer-disabled:peer-placeholder-shown:text-blue-gray-500 transition-all -top-1.5 "
                                "peer-placeholder-shown:text-sm text-[11px] peer-focus:text-[11px] before:content["
                                "' '] before:block before:box-border before:w-2.5 before:h-1.5 before:mt-[6.5px] "
                                "before:mr-1 peer-placeholder-shown:before:border-transparent before:rounded-tl-md "
                                "before:border-t peer-focus:before:border-t-2 before:border-l "
                                "peer-focus:before:border-l-2 before:pointer-events-none before:transition-all "
                                "peer-disabled:before:border-transparent after:content[' '] after:block "
                                "after:flex-grow after:box-border after:w-2.5 after:h-1.5 after:mt-[6.5px] "
                                "after:ml-1 peer-placeholder-shown:after:border-transparent after:rounded-tr-md "
                                "after:border-t peer-focus:after:border-t-2 after:border-r "
                                "peer-focus:after:border-r-2 after:pointer-events-none after:transition-all "
                                "peer-disabled:after:border-transparent peer-placeholder-shown:leading-[3.75] "
                                "text-gray-500 peer-focus:text-gray-900 before:border-gray-200 "
                                "peer-focus:before:!border-gray-900 after:border-gray-200 "
                                "peer-focus:after:!border-gray-900"
                            )
                        )
                elif field.type == "TextAreaField":
                    with div(
                        class_name="relative w-full min-w-[200px]",
                    ):
                        raw(
                            field(
                                placeholder=" ",
                                class_="peer h-full min-h-[100px] w-full resize-none rounded-[7px] border "
                                "border-gray-200 bg-transparent px-3 py-2.5 font-sans text-sm font-normal "
                                "text-blue-gray-700 outline outline-0 transition-all placeholder-shown:border "
                                "placeholder-shown:border-gray-200 placeholder-shown:border-t-gray-200 "
                                "focus:border-2 focus:border-gray-900 focus:border-t-transparent border-t-transparent "
                                "focus:outline-0"
                                "disabled:resize-none disabled:border-0 disabled:bg-blue-gray-50",
                            )
                        )
                        raw(
                            field.label(
                                class_="before:content[' '] after:content[' '] pointer-events-none absolute left-0 "
                                "-top-1.5 flex h-full w-full select-none text-[11px] font-normal leading-tight "
                                "text-blue-gray-400 transition-all before:pointer-events-none before:mt-[6.5px] "
                                "before:mr-1 before:box-border before:block before:h-1.5 before:w-2.5 "
                                "before:rounded-tl-md before:border-t before:border-l before:border-gray-200 "
                                "before:transition-all after:pointer-events-none after:mt-[6.5px] after:ml-1 "
                                "after:box-border after:block after:h-1.5 after:w-2.5 after:flex-grow "
                                "after:rounded-tr-md after:border-t after:border-r after:border-gray-200 "
                                "after:transition-all peer-placeholder-shown:text-sm "
                                "peer-placeholder-shown:leading-[3.75] peer-placeholder-shown:text-blue-gray-500 "
                                "peer-placeholder-shown:before:border-transparent "
                                "peer-placeholder-shown:after:border-transparent peer-focus:text-[11px] "
                                "peer-focus:leading-tight peer-focus:text-gray-900 peer-focus:before:border-t-2 "
                                "peer-focus:before:border-l-2 peer-focus:before:border-gray-900 "
                                "peer-focus:after:border-t-2 peer-focus:after:border-r-2 "
                                "peer-focus:after:border-gray-900 peer-disabled:text-transparent "
                                "peer-disabled:before:border-transparent peer-disabled:after:border-transparent "
                                "peer-disabled:peer-placeholder-shown:text-blue-gray-500"
                            )
                        )
                elif field.type == "SelectField":
                    with div(
                        class_name="relative w-full min-w-[200px] h-10",
                    ):
                        raw(
                            field(
                                placeholder=" ",
                                class_="peer w-full h-full bg-transparent text-blue-gray-700 font-sans font-normal "
                                "outline outline-0 focus:outline-0 disabled:bg-blue-gray-50 disabled:border-0 "
                                "transition-all placeholder-shown:border placeholder-shown:border-gray-200 "
                                "placeholder-shown:border-t-gray-200 border focus:border-2 "
                                "border-t-transparent focus:border-t-transparent text-sm px-3 py-2.5 rounded-[7px] "
                                "border-gray-200 focus:border-gray-900",
                            )
                        )
                        raw(
                            field.label(
                                class_="before:content[' '] after:content[' '] pointer-events-none absolute left-0 "
                                "-top-1.5 flex h-full w-full select-none text-[11px] font-normal leading-tight "
                                "text-blue-gray-400 transition-all before:pointer-events-none before:mt-["
                                "6.5px] before:mr-1 before:box-border before:block before:h-1.5 before:w-2.5 "
                                "before:rounded-tl-md before:border-t before:border-l "
                                "before:border-blue-gray-200 before:transition-all after:pointer-events-none "
                                "after:mt-[6.5px] after:ml-1 after:box-border after:block after:h-1.5 "
                                "after:w-2.5 after:flex-grow after:rounded-tr-md after:border-t after:border-r "
                                "after:border-blue-gray-200 after:transition-all "
                                "peer-placeholder-shown:text-sm peer-placeholder-shown:leading-[3.75] "
                                "peer-placeholder-shown:text-blue-gray-500 "
                                "peer-placeholder-shown:before:border-transparent "
                                "peer-placeholder-shown:after:border-transparent peer-focus:text-[11px] "
                                "peer-focus:leading-tight peer-focus:text-gray-900 "
                                "peer-focus:before:border-t-2 peer-focus:before:border-l-2 "
                                "peer-focus:before:border-gray-900 peer-focus:after:border-t-2 "
                                "peer-focus:after:border-r-2 peer-focus:after:border-gray-900 "
                                "peer-disabled:text-transparent peer-disabled:before:border-transparent "
                                "peer-disabled:after:border-transparent "
                                "peer-disabled:peer-placeholder-shown:text-blue-gray-500"
                            )
                        )
            if with_submit_button:
                button(
                    "Zapisz",
                    type="submit",
                    class_name="align-middle select-none font-sans font-bold text-center uppercase transition-all "
                    "disabled:opacity-50 disabled:shadow-none disabled:pointer-events-none text-xs py-3 "
                    "px-6 rounded-lg bg-pink-500 text-white shadow-md shadow-gray-900/10 hover:shadow-lg "
                    "hover:shadow-gray-900/20 focus:opacity-[0.85] focus:shadow-none active:opacity-[0.85] "
                    "active:shadow-none block w-full",
                )
    return form_
