from typing import Optional

from pydantic import BaseModel

from .utils import get_js_file


class Page(BaseModel):
    name: str
    path: str
    title: Optional[str] = ""
    template_path: Optional[str] = ""
    js_file: Optional[str] = None


HOME_PAGE = Page(
    name="home",
    path="/",
    title="Home",
    template_path="pages/home.html",
    js_file=get_js_file(ts_filepath="pages/home.ts"),
)
MORE_PAGE = Page(
    name="more",
    path="/more",
    title="More",
    template_path="pages/more.html",
    js_file=get_js_file(ts_filepath="pages/more.ts"),
)
