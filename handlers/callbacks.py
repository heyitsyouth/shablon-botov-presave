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

    await callback.answer()

