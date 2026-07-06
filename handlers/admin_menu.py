"""
handlers/admin_menu.py

Главное меню администратора.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import ADMIN_IDS
from database import db
from keyboards import get_admin_keyboard

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_panel(message: Message):

    if not is_admin(message.from_user.id):
        return

    stats = await db.statistics()

    text = (
        "⚙️ <b>Панель администратора</b>\n\n"
        f"👥 Всего участников: <b>{stats['total']}</b>\n"
        f"📅 Сегодня: <b>{stats['today']}</b>\n\n"
        "Выберите действие:"
    )

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )
