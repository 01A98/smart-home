from functools import cached_property
from typing import Optional

from pydantic import BaseModel, computed_field
from sanic import Sanic

from src.components import navbar
from src.settings import SETTINGS, Settings


class Page(BaseModel):
    name: str
    title: Optional[str] = ""
    template_path: Optional[str] = ""
    js_file: Optional[str] = None


# Used for navbar, entries will be added in individual views
NAVIGATION: dict[str, Page] = {}


class BaseContext(BaseModel):
    app: Sanic
    current_page: Optional[Page] = None
    navigation: dict[str, Page] = NAVIGATION
    settings: Settings = SETTINGS

    @computed_field
    @cached_property
    def app_navbar(self) -> str:
        return str(navbar(self.app, self.navigation, self.current_page))

    class Config:
        arbitrary_types_allowed = True


def create_views(app: Sanic) -> None:
    from .home.home import create_view as create_home_view
    from .bulbs.bulbs import create_view as create_bulbs_view
    from .bulbs.id.bulb import create_view as create_bulbs_id_view
    from .rooms.rooms import create_view as create_rooms_view
    from .rooms.id.room import create_view as create_rooms_id_view
    from .more.more import create_view as create_more_view

    create_home_view(app)
    create_bulbs_view(app)
    create_bulbs_id_view(app)
    create_rooms_view(app)
    create_rooms_id_view(app)
    create_more_view(app)
