from typing import Optional
from pydantic import BaseModel


class Page(BaseModel):
    name: str
    path: str
    title: Optional[str] = ""


class Pages(BaseModel):
    HOME: Page = Page(name="home", path="/", title="Home")
    MORE: Page = Page(name="more", path="/more", title="More")


PAGES = Pages()
