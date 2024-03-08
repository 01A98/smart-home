from dominate.tags import a, span


class NewItemButton(a):
    tagname = "a"
    id = "new-item-button"

    def __init__(self, href: str = None) -> None:
        super().__init__()

        self["href"] = href

        with self:
            span(
                "+ Dodaj Nowy",
                class_name="self-center text-white bg-pink-500 hover:bg-pink-600 focus:outline-none "
                           "focus:ring-4 focus:ring-purple-300 font-medium rounded-md text-md px-4 py-3 "
                           "text-center mb-4",
                role="button",
                aria_label="Add new item",

            )
