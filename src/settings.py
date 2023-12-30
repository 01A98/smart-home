import os
from typing import Optional

from pydantic_core import Url
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str
    db_url: Optional[Url] = Url("sqlite://db.sql")
    static_redirects: dict[str, str] = {
        "/home": "/",
    }


SETTINGS = Settings(env=os.getenv("ENV", "dev"))
