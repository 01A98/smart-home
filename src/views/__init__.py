from typing import Optional

from pydantic import BaseModel

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
