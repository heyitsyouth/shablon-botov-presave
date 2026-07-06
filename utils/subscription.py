"""
subscription.py

Проверка подписки пользователя.

Если check_subscription=False,
функция всегда возвращает True.

Это позволяет использовать
один и тот же код
для разных розыгрышей.
"""

from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from aiogram.exceptions import TelegramBadRequest

from config import CONFIG, REQUIRED_CHANNELS

logger = logging.getLogger(__name__)


ALLOWED_STATUSES = {
    ChatMemberStatus.MEMBER,
    ChatMemberStatus.ADMINISTRATOR,
    ChatMemberStatus.CREATOR,
}


async def check_subscription(
    bot: Bot,
    user_id: int,
) -> bool:
    """
    Проверить подписку пользователя.

    Если проверка выключена,
    всегда возвращает True.
    """

    if not CONFIG.get("check_subscription", False):
        return True

    for channel in REQUIRED_CHANNELS:

        try:

            chat = channel["id"]

            if chat is None:
                chat = f"@{channel['username']}"

            member = await bot.get_chat_member(
                chat,
                user_id,
            )

            if member.status not in ALLOWED_STATUSES:
                return False

        except TelegramBadRequest:

            logger.exception(
                "Unable to check subscription."
            )

            return False

        except Exception:

            logger.exception(
                "Unexpected subscription error."
            )

            return False

    return True
