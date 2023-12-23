from typing import Optional
from pydantic import BaseModel


class Page(BaseModel):
    name: str
    path: str
    title: Optional[str] = ""
    file_path: Optional[str] = ""


class Pages(BaseModel):
    HOME: Page = Page(name="home", path="/", title="Home", file_path="pages/home.html")
    MORE: Page = Page(
        name="more", path="/more", title="More", file_path="pages/more.html"
    )


PAGES = Pages()
