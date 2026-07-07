"""
handlers/callbacks.py

Обработчики inline-кнопок.
"""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "cancel")
async def cancel(
    callback: CallbackQuery,
    state: FSMContext,
):
    """
    Отмена текущего действия.
    """

    await state.clear()

    await callback.message.edit_reply_markup()

    await callback.message.answer(
        "❌ Действие отменено."
    )

    from config import ADMIN_IDS

    if callback.from_user.id in ADMIN_IDS:

        from database import db

        from keyboards import get_admin_keyboard

        stats = await db.statistics()

        text = (
            "⚙️ <b>Панель администратора</b>\n\n"
            f"👥 Всего участников: <b>{stats['total']}</b>\n"
            f"📅 Сегодня: <b>{stats['today']}</b>\n\n"
            "Выберите действие:"
        )

        await callback.message.answer(
            text,
            parse_mode="HTML",
            reply_markup=get_admin_keyboard(),
        )

    await callback.answer()


