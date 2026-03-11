import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str
    admin_ids: list[int]
    db_path: str = "bot.db"


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    admin_ids_raw = os.getenv("ADMIN_IDS", "").strip()

    if not bot_token:
        raise ValueError("BOT_TOKEN topilmadi.")

    if not admin_ids_raw:
        raise ValueError("ADMIN_IDS topilmadi.")

    admin_ids = []
    for item in admin_ids_raw.split(","):
        item = item.strip()
        if item.isdigit():
            admin_ids.append(int(item))

    if not admin_ids:
        raise ValueError("ADMIN_IDS noto'g'ri.")

    return Config(
        bot_token=bot_token,
        admin_ids=admin_ids,
    )
