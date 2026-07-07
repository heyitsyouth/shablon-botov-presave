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

from config import BOT_TOKEN, REDIS_URL
from database import db
from scheduler import scheduler

from handlers.start import router as start_router
from handlers.screenshots import router as screenshots_router
from handlers.callbacks import router as callbacks_router

from handlers.admin_menu import router as admin_menu_router
from handlers.admin_texts import router as admin_texts_router
from handlers.admin_draw import router as admin_draw_router
from handlers.admin_broadcast import router as admin_broadcast_router
from handlers.admin_export import router as admin_export_router


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

    # Настройка FSM-хранилища (Redis для 50k+ нагрузки, MemoryStorage как фолбек)
    if REDIS_URL:
        try:
            from aiogram.fsm.storage.redis import RedisStorage
            from redis.asyncio import Redis
            redis_client = Redis.from_url(REDIS_URL)
            storage = RedisStorage(redis_client)
            logging.info("FSM storage: Redis")
        except Exception as e:
            logging.error(f"Failed to load RedisStorage, falling back to MemoryStorage: {e}")
            from aiogram.fsm.storage.memory import MemoryStorage
            storage = MemoryStorage()
    else:
        from aiogram.fsm.storage.memory import MemoryStorage
        storage = MemoryStorage()
        logging.info("FSM storage: Memory")

    dp = Dispatcher(storage=storage)

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
    dp.include_router(admin_export_router)

    #
    # База данных
    #

    await db.connect()

    #
    # Планировщик
    #

    await scheduler.start(bot)

    logging.info("Bot started.")

    try:

        await dp.start_polling(bot)

    finally:

        await scheduler.stop()

        await db.close()

        await bot.session.close()



if __name__ == "__main__":

    asyncio.run(main())
