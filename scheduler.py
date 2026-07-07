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

from config import CONFIG, ADMIN_IDS, save_config
from database import db
from utils.draw import choose_winners

logger = logging.getLogger(__name__)


class Scheduler:

    def __init__(self):

        self.task = None

        self.running = False

        self.bot = None

    async def start(self, bot):

        """
        Запустить планировщик.
        """

        if self.running:
            return

        self.running = True

        self.bot = bot

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
            "Contest end reached. Running auto-draw."
        )

        # Выбираем победителей
        participants = await db.get_all_participants()
        winners_count = CONFIG.get("winners_count", 1)

        if not participants:
            winners_text = "❌ <b>[Авто-розыгрыш]</b> Участники отсутствуют."
        else:
            winners = choose_winners(participants, winners_count)
            winners_text = (
                f"🏆 <b>[Авто-розыгрыш] Результаты розыгрыша:</b>\n\n"
                f"Всего участников: <b>{len(participants)}</b>\n"
                f"Победители:\n\n"
            )
            for i, winner in enumerate(winners, start=1):
                username = winner.get("username")
                if username:
                    winners_text += f"{i}. @{username} (ID: <code>{winner['user_id']}</code>)\n"
                else:
                    winners_text += f"{i}. {winner['full_name']} (ID: <code>{winner['user_id']}</code>)\n"

        # Отправляем результаты всем администраторам
        if self.bot:
            for admin_id in ADMIN_IDS:
                try:
                    await self.bot.send_message(
                        chat_id=admin_id,
                        text=winners_text,
                        parse_mode="HTML",
                    )

                    # Отправляем скриншоты победителей
                    if participants and winners:
                        for i, winner in enumerate(winners, start=1):
                            username = winner.get("username")
                            user_info = f"@{username}" if username else winner['full_name']
                            caption = f"🏆 Победитель #{i}: {user_info} (ID: <code>{winner['user_id']}</code>)"
                            try:
                                await self.bot.send_photo(
                                    chat_id=admin_id,
                                    photo=winner['telegram_file_id'],
                                    caption=caption,
                                    parse_mode="HTML"
                                )
                            except Exception as photo_err:
                                logger.error(
                                    f"Failed to send winner screenshot to admin {admin_id}: {photo_err}"
                                )
                except Exception as e:
                    logger.error(
                        f"Failed to send auto-draw results to admin {admin_id}: {e}"
                    )

        # Сбрасываем дату розыгрыша в конфиге, чтобы не повторять его
        CONFIG["broadcast_date"] = ""
        save_config(CONFIG)
        logger.info("Auto-draw completed. broadcast_date cleared in config.json.")


scheduler = Scheduler()


