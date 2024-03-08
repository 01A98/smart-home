from dominate.tags import div, h3, p


class NothingHere(div):
    tagname = "div"
    id = "app-nothing-here-message"

    def __init__(self, title: str = "Pusto :>", detail: str = "Może pora coś tutaj dodać.") -> None:
        super().__init__()

        self["class"] = "mb-4 mx-auto max-w-screen-sm flex flex-col gap-2 justify-center items-center"

        with self:
            h3(title, class_name="mb-4 text-3xl tracking-tight font-bold text-gray-900 md:text-4xl dark:text-white")
            p(detail, class_name="mb-4 text-lg font-light text-gray-500 dark:text-gray-400 mx-4")
