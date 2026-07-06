"""
scheduler.py

Планировщик автоматических задач.

Отвечает за:

• автоматическое завершение конкурса
• автоматическую рассылку
• автоматический розыгрыш (если включено)

Работает в отдельной asyncio-задаче.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from config import CONFIG

logger = logging.getLogger(__name__)


class Scheduler:

    def __init__(self):

        self.task = None

        self.running = False

    async def start(self):

        """
        Запустить планировщик.
        """

        if self.running:
            return

        self.running = True

        self.task = asyncio.create_task(
            self._loop()
        )

        logger.info("Scheduler started.")

    async def stop(self):

        """
        Остановить планировщик.
        """

        self.running = False

        if self.task:

            self.task.cancel()

            try:

                await self.task

            except asyncio.CancelledError:

                pass

        logger.info("Scheduler stopped.")

    async def _loop(self):

        """
        Главный цикл.

        Проверяет дату окончания
        конкурса раз в минуту.
        """

        while self.running:

            try:

                await self.check()

            except Exception:

                logger.exception(
                    "Scheduler error"
                )

            await asyncio.sleep(60)

    async def check(self):

        """
        Проверка даты конкурса.
        """

        draw_date = CONFIG.get(
            "broadcast_date"
        )

        if not draw_date:
            return

        try:

            target = datetime.fromisoformat(
                draw_date
            )

        except ValueError:

            logger.error(
                "Invalid broadcast_date."
            )

            return

        now = datetime.now(
            target.tzinfo
        )

        if now < target:
            return

        logger.info(
            "Contest end reached."
        )

        #
        # Здесь позже будут вызваны:
        #
        # await broadcast(...)
        #
        # await draw(...)
        #
        # После чего дата конкурса
        # будет обновлена.
        #

        self.running = False


scheduler = Scheduler()
