from typing import Optional

from dominate.tags import span


class Icon(span):
    tagname = "span"

    def __init__(self, name: str, class_name: Optional[str] = "material-icons-round", **kwargs):
        super().__init__(name, **{"class_name": class_name, **kwargs})
