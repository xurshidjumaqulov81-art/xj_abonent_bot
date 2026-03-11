import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.config import load_config
from app.handlers import user


async def start():
    config = load_config()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    dp.include_router(user.router)

    print("Bot ishga tushdi...")

    await dp.start_polling(bot)


def main():
    asyncio.run(start())
