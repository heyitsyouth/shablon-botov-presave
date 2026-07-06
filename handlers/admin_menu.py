"""
handlers/admin_menu.py

Главное меню администратора.
"""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import ADMIN_IDS
from database import db
from keyboards import get_admin_keyboard

logger = logging.getLogger(__name__)

router = Router()


def is_admin(user_id: int) -> bool:
    """
    Проверка администратора.
    """
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_panel(message: Message):
    """
    Открыть панель администратора.
    """

    if not is_admin(message.from_user.id):
        return

    stats = await db.statistics()

    text = (
        "⚙️ <b>Панель администратора</b>\n\n"
        f"👥 Всего участников: <b>{stats['total']}</b>\n"
        f"📅 Сегодня зарегистрировалось: <b>{stats['today']}</b>"
    )

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """
    Показать статистику.
    """

    if not is_admin(callback.from_user.id):
        return

    stats = await db.statistics()

    text = (
        "📊 <b>Статистика конкурса</b>\n\n"
        f"👥 Всего участников: <b>{stats['total']}</b>\n"
        f"📅 Сегодня: <b>{stats['today']}</b>"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )

    await callback.answer()
