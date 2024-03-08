from dominate.tags import span


class Icon(span):
    tagname = "span"

    def __init__(self, name: str, **kwargs):
        super().__init__(name, class_name="material-icons-round", **kwargs)
