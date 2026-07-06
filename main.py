"""
main.py

Точка входа проекта.
"""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN
from database import db
from scheduler import scheduler

from handlers.start import router as start_router
from handlers.screenshots import router as screenshots_router
from handlers.callbacks import router as callbacks_router

from handlers.admin_menu import router as admin_menu_router
from handlers.admin_texts import router as admin_texts_router
from handlers.admin_draw import router as admin_draw_router
from handlers.admin_broadcast import router as admin_broadcast_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


async def main():

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
        ),
    )

    dp = Dispatcher()

    #
    # Пользовательские роутеры
    #

    dp.include_router(start_router)
    dp.include_router(callbacks_router)
    dp.include_router(screenshots_router)

    #
    # Админка
    #

    dp.include_router(admin_menu_router)
    dp.include_router(admin_texts_router)
    dp.include_router(admin_draw_router)
    dp.include_router(admin_broadcast_router)

    #
    # База данных
    #

    await db.connect()

    #
    # Планировщик
    #

    await scheduler.start()

    logging.info("Bot started.")

    try:

        await dp.start_polling(bot)

    finally:

        await scheduler.stop()

        await db.close()

        await bot.session.close()


if __name__ == "__main__":

    asyncio.run(main())
