from typing import Optional

from pydantic import BaseModel
from sanic import Sanic

from src.settings import SETTINGS, Settings
from src.utils import get_js_file


class Page(BaseModel):
    name: str
    path: str
    title: Optional[str] = ""
    template_path: Optional[str] = ""
    js_file: Optional[str] = None


# Used for navbar, entries will be added in individual views
NAVIGATION: dict[str, Page] = {}


class PageContext(BaseModel):
    current_page: Optional[Page] = None
    navigation: dict[str, Page] = NAVIGATION
    base_js: str = get_js_file(ts_filepath="base.ts")
    settings: Settings = SETTINGS

    class Config:
        arbitrary_types_allowed = True


def create_views(app: Sanic) -> None:
    from .home.home import create_view as create_home_view
    from .bulbs.bulbs import create_view as create_bulbs_view
    from .bulbs.id.bulbs import create_view as create_bulbs_id_view
    from .rooms.rooms import create_view as create_rooms_view
    from .rooms.id.rooms import create_view as create_rooms_id_view
    from .more.more import create_view as create_more_view

    create_home_view(app)
    create_bulbs_view(app)
    create_bulbs_id_view(app)
    create_rooms_view(app)
    create_rooms_id_view(app)
    create_more_view(app)
