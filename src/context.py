import os
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from .pages import HOME_PAGE, MORE_PAGE, Page

from .utils import get_js_file


class Settings(BaseSettings):
    env: str


class PageContext(BaseModel):
    current_page: Page
    pages: list[Page] = [
        HOME_PAGE,
        MORE_PAGE,
    ]
    base_js: str = get_js_file(ts_filepath="base.ts")
    settings: Settings = Settings(env=os.getenv("ENV", "dev"))

    class Config:
        arbitrary_types_allowed = True
