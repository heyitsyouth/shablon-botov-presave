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


def choose_winners(participants: List[dict], count: int) -> List[dict]:
    """
    Выбирает случайных победителей из списка участников.
    """

    if not participants:
        return []

    if count >= len(participants):
        return list(participants)

    return random.sample(
        participants,
        count,
    )


async def draw_winners(count: int) -> List[dict]:
    """
    Выбирает случайных победителей из БД.
    """

    participants = await db.get_all_participants()

    return choose_winners(participants, count)


async def participant_count() -> int:
    """
    Возвращает количество участников.
    """

    stats = await db.statistics()

    return stats.get("total", 0)


async def get_statistics() -> dict:
    """
    Возвращает статистику конкурса.
    """

    return await db.statistics()

