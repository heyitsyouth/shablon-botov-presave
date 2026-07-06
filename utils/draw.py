"""
draw.py

Логика проведения розыгрыша.

Файл не зависит от Telegram.
Он работает только с базой данных.
"""

from __future__ import annotations

import random
from typing import List

from database import db


async def draw_winners(count: int) -> List[dict]:
    """
    Выбирает случайных победителей.

    Parameters
    ----------
    count : int
        Количество победителей.

    Returns
    -------
    list
        Список победителей.
    """

    participants = await db.get_all()

    if not participants:
        return []

    if count >= len(participants):
        return list(participants)

    return random.sample(
        list(participants),
        count,
    )


async def participant_count() -> int:
    """
    Возвращает количество участников.
    """

    return await db.count()


async def get_statistics() -> dict:
    """
    Возвращает статистику конкурса.
    """

    return await db.statistics()
