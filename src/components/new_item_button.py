from dominate.tags import a, span


class NewItemButton(a):
    tagname = "span"
    id = "new-item-button"

    def __init__(self, href: str = None) -> None:
        super().__init__()

        self["class"] = (
            "text-white bg-pink-500 hover:bg-pink-600 focus:outline-none focus:ring-4 "
            "focus:ring-purple-300 font-medium rounded-md text-md p-4 text-center"
        )
        self["role"] = "button"
        self["aria-label"] = "Add new item"

        with self:
            a(
                "+ Dodaj Nowy",
                href=href,
            )
