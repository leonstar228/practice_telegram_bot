import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class Settings:
    bot_token: str
    admin_ids: list[int]
    weather_api_key: str
    db_path: str

def parse_admin_ids(value: str) -> list[int]:
    if not value:
        return []
    return [int(item.strip()) for item in value.split(",") if item.strip().isdigit()]

settings = Settings(
    bot_token=os.getenv("BOT_TOKEN", ""),
    admin_ids=parse_admin_ids(os.getenv("ADMIN_IDS", "")),
    weather_api_key=os.getenv("WEATHER_API_KEY", ""),
    db_path=os.getenv("DB_PATH", "bot.db"),
)

if not settings.bot_token:
    raise RuntimeError("BOT_TOKEN is not set")
