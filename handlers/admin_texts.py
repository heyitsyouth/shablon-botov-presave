"""
handlers/admin_texts.py

Редактирование всех текстов конкурса.
"""

from __future__ import annotations

import json
from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import ADMIN_IDS, CONFIG, save_config
from keyboards import get_cancel_keyboard
from states import AdminStates

router = Router()



@router.callback_query(F.data == "admin_texts")
async def texts_menu(callback: CallbackQuery):

    if callback.from_user.id not in ADMIN_IDS:
        return

    text = (
        "📝 <b>Редактирование текстов</b>\n\n"

        "Отправьте:\n\n"

        "1 — стартовый текст\n"

        "2 — инструкция\n"

        "3 — текст благодарности\n"

        "4 — ссылка на пресейв\n"

        "5 — текст рассылки"
    )

    await callback.message.answer(
        text,
        parse_mode="HTML",
    )

    await callback.answer()


@router.message(F.text == "1")
async def edit_start(
    message: Message,
    state: FSMContext,
):

    if message.from_user.id not in ADMIN_IDS:
        return

    await state.set_state(
        AdminStates.waiting_start_text
    )

    await message.answer(
        "Отправьте новый стартовый текст.",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(AdminStates.waiting_start_text)
async def save_start(
    message: Message,
    state: FSMContext,
):

    CONFIG["start_text"] = message.html_text

    save_config(CONFIG)

    await state.clear()

    await message.answer(
        "✅ Стартовый текст обновлён."
    )


@router.message(F.text == "2")
async def edit_instruction(
    message: Message,
    state: FSMContext,
):

    if message.from_user.id not in ADMIN_IDS:
        return

    await state.set_state(
        AdminStates.waiting_instruction_text
    )

    await message.answer(
        "Отправьте новую инструкцию."
    )


@router.message(AdminStates.waiting_instruction_text)
async def save_instruction(
    message: Message,
    state: FSMContext,
):

    CONFIG["instruction_text"] = message.html_text

    save_config(CONFIG)

    await state.clear()

    await message.answer(
        "✅ Инструкция обновлена."
    )


@router.message(F.text == "3")
async def edit_thanks(
    message: Message,
    state: FSMContext,
):

    if message.from_user.id not in ADMIN_IDS:
        return

    await state.set_state(
        AdminStates.waiting_thank_you_text
    )

    await message.answer(
        "Отправьте новый текст благодарности."
    )


@router.message(AdminStates.waiting_thank_you_text)
async def save_thanks(
    message: Message,
    state: FSMContext,
):

    CONFIG["thank_you_text"] = message.html_text

    save_config(CONFIG)

    await state.clear()

    await message.answer(
        "✅ Текст обновлён."
    )


@router.message(F.text == "4")
async def edit_url(
    message: Message,
    state: FSMContext,
):

    if message.from_user.id not in ADMIN_IDS:
        return

    await state.set_state(
        AdminStates.waiting_presave_url
    )

    await message.answer(
        "Пришлите новую ссылку."
    )


@router.message(AdminStates.waiting_presave_url)
async def save_url(
    message: Message,
    state: FSMContext,
):

    CONFIG["presave_url"] = message.text.strip()

    save_config(CONFIG)

    await state.clear()

    await message.answer(
        "✅ Ссылка обновлена."
    )


@router.message(F.text == "5")
async def edit_broadcast(
    message: Message,
    state: FSMContext,
):

    if message.from_user.id not in ADMIN_IDS:
        return

    await state.set_state(
        AdminStates.waiting_broadcast_text
    )

    await message.answer(
        "Отправьте новый текст рассылки."
    )


@router.message(AdminStates.waiting_broadcast_text)
async def save_broadcast(
    message: Message,
    state: FSMContext,
):

    CONFIG["broadcast_text"] = message.html_text

    save_config(CONFIG)

    await state.clear()

    await message.answer(
        "✅ Текст рассылки обновлён."
    )
