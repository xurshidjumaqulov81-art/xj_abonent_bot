import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str
    admin_id: int
    db_path: str = "bot.db"


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    admin_id_raw = os.getenv("ADMIN_ID", "").strip()

    if not bot_token:
        raise ValueError("BOT_TOKEN topilmadi.")
    if not admin_id_raw.isdigit():
        raise ValueError("ADMIN_ID noto'g'ri.")

    return Config(
        bot_token=bot_token,
        admin_id=int(admin_id_raw),
    )
