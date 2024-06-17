from dominate.tags import a


class NewItemButton(a):
    tagname = "a"
    id = "new-item-button"

    def __init__(self, href: str = None) -> None:
        super().__init__("+ Dodaj Nowy")

        self["href"] = href
        self["class"] = (
            "text-white bg-pink-500 hover:bg-pink-600 focus:outline-none focus:ring-4 "
            "focus:ring-purple-300 font-medium rounded-md text-md p-4 text-center"
        )
        self["role"] = "button"
        self["aria-label"] = "Add new item"
        # self["data-ripple-dark"] = "true"
        # self["data-ripple-light"] = "true"
