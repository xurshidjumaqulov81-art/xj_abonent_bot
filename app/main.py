import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import load_config
from app.db import init_db
from app.handlers.user import router as user_router
from app.handlers.admin import router as admin_router


async def start_bot():
    config = load_config()
    init_db()

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()
    dp.include_router(user_router)
    dp.include_router(admin_router)

    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


def main():
    asyncio.run(start_bot())
