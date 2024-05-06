import os
from typing import Optional

from pydantic_core import Url
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str
    db_url: Optional[Url] = Url("sqlite://db.sql")
    static_redirects: dict[str, str] = {"/home": "/"}
    temperature_settings: list[tuple[str, str]] = [
        ("warmest", "Najcieplejszy"),
        ("warmer", "Cieplejszy"),
        ("warm", "Ciepły"),
        ("cold", "Chłodny"),
        ("colder", "Chłodniejszy"),
        ("coldest", "Najchłodniejszy"),
    ]
    scenes: list[tuple[str, str]] = [
        ("1", "Ocean"),
        ("2", "Romance"),
        ("3", "Sunset"),
        ("4", "Party"),
        ("5", "Fireplace"),
        ("6", "Cozy"),
        ("7", "Forest"),
        ("8", "Pastel Colors"),
        ("9", "Wake up"),
        ("10", "Bedtime"),
        ("11", "Warm white"),
        ("12", "Daylight"),
        ("13", "Cool white"),
        ("14", "Night light"),
        ("15", "Focus"),
        ("16", "Relax"),
        ("17", "True colors"),
        ("18", "TV Time"),
        ("19", "Plant growth"),
        ("20", "Spring"),
        ("21", "Summer"),
        ("22", "Fall"),
        ("23", "Deep dive"),
        ("24", "Jungle"),
        ("25", "Mojito"),
        ("26", "Club"),
        ("27", "Christmas"),
        ("28", "Halloween"),
        ("29", "Candlelight"),
        ("30", "Golden white"),
        ("31", "Pulse"),
        ("32", "Steampunk"),
        ("33", "Diwali"),
    ]


SETTINGS = Settings(env=os.getenv("ENV", "dev"))
