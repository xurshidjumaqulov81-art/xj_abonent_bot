import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str
    admin_ids: list


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN")
    admin_ids = os.getenv("ADMIN_IDS")

    return Config(
        bot_token=bot_token,
        admin_ids=[int(x) for x in admin_ids.split(",")]
    )
