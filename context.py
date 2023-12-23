from pydantic import BaseModel
from pydantic_settings import BaseSettings

from config import PAGES, Page, Pages


class Settings(BaseSettings):
    env: str


class PageContext(BaseModel):
    current_page: Page
    pages: Pages = PAGES
    settings: Settings = Settings()

    class Config:
        arbitrary_types_allowed = True
