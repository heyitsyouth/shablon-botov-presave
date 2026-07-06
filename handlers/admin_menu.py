"""
handlers/admin_menu.py

Главное меню администратора.
"""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import F

from config import ADMIN_IDS
from database import db
from keyboards import get_admin_keyboard
from utils.export_csv import export_participants

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
        f"📅 Сегодня: <b>{stats['today']}</b>"
    )

    await message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )


@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        return

    stats = await db.statistics()

    text = (
        "📊 <b>Статистика</b>\n\n"
        f"👥 Всего участников: <b>{stats['total']}</b>\n"
        f"📅 Сегодня: <b>{stats['today']}</b>"
    )

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard(),
    )

    await callback.answer()


@router.callback_query(F.data == "admin_export_csv")
async def export_csv(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        return

    file_path = await export_participants()

    await callback.message.answer_document(
        FSInputFile(file_path),
        caption="📥 Экспорт участников конкурса",
    )

    await callback.answer()


@router.callback_query(F.data == "admin_texts")
async def open_texts(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        return

    await callback.message.answer(
        "📝 Раздел редактирования текстов.\n"
        "Используйте кнопки и команды этого раздела."
    )

    await callback.answer()


@router.callback_query(F.data == "admin_draw")
async def open_draw(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        return

    await callback.message.answer(
        "🎲 Раздел управления розыгрышем."
    )

    await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
async def open_broadcast(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        return

    await callback.message.answer(
        "📣 Раздел массовой рассылки."
    )

    await callback.answer()
