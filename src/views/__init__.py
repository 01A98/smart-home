from functools import cached_property
from typing import Optional

from dominate.tags import html_tag
from pydantic import BaseModel, computed_field
from sanic import Sanic

from src.components.navbar import Navbar
from src.settings import SETTINGS, Settings


class Page(BaseModel):
    name: str
    title: Optional[str] = ""`
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
    def app_navbar(self) -> html_tag:
        return Navbar(self.app, self.navigation, self.current_page)

    class Config:
        arbitrary_types_allowed = True
