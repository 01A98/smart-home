from __future__ import annotations

from glob import glob
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .context import Page


def get_js_file(page: Optional[Page] = None, ts_filepath: Optional[str] = None):
    if ts_filepath:
        js_glob_path = "public" + "/" + ts_filepath.replace(".ts", ".*.js")
        return glob(js_glob_path)[0]
    elif page:
        html_path = page.template_path
        if html_path:
            js_glob_path = "public" + "/" + html_path.replace(".html", ".*.js")
            return glob(js_glob_path)[0]
    raise ValueError("Must provide either page object or ts_filepath")
