"""
handlers/admin_draw.py

Управление розыгрышем.

Функции:
• изменение даты окончания конкурса
• изменение количества победителей
• ручной запуск розыгрыша
"""

from __future__ import annotations

from datetime import datetime
import json

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import CONFIG, ADMIN_IDS
from database import db
from states import AdminStates
from utils.draw import choose_winners

router = Router()


CONFIG_PATH = "config.json"


def save_config():
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(
            CONFIG,
            f,
            ensure_ascii=False,
            indent=2,
        )


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ===============================
# Меню розыгрыша
# ===============================

@router.callback_query(F.data == "admin_draw")
async def draw_menu(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        return

    text = (
        "🎲 <b>Настройки розыгрыша</b>\n\n"
        f"📅 Дата:\n{CONFIG['broadcast_date']}\n\n"
        f"🏆 Победителей: {CONFIG['winners_count']}\n\n"
        "Что хотите изменить?"
    )

    await callback.message.answer(
        text,
        parse_mode="HTML",
    )

    await callback.message.answer(
        "Напишите:\n\n"
        "1 — изменить дату\n"
        "2 — изменить количество победителей\n"
        "3 — провести розыгрыш сейчас"
    )

    await callback.answer()


# ===============================
# ДАТА
# ===============================

@router.message(F.text == "1")
async def edit_date(
    message: Message,
    state: FSMContext,
):

    if not is_admin(message.from_user.id):
        return

    await state.set_state(
        AdminStates.waiting_broadcast_date
    )

    await message.answer(
        "Введите новую дату.\n\n"
        "Пример:\n"
        "2026-12-31T20:00:00+03:00"
    )


@router.message(AdminStates.waiting_broadcast_date)
async def save_date(
    message: Message,
    state: FSMContext,
):

    try:
        datetime.fromisoformat(message.text.strip())

    except Exception:

        await message.answer(
            "❌ Неверный формат даты."
        )

        return

    CONFIG["broadcast_date"] = message.text.strip()

    save_config()

    await state.clear()

    await message.answer(
        "✅ Дата обновлена."
    )


# ===============================
# КОЛИЧЕСТВО ПОБЕДИТЕЛЕЙ
# ===============================

@router.message(F.text == "2")
async def edit_count(
    message: Message,
    state: FSMContext,
):

    if not is_admin(message.from_user.id):
        return

    await state.set_state(
        AdminStates.waiting_winners_count
    )

    await message.answer(
        "Введите количество победителей."
    )


@router.message(AdminStates.waiting_winners_count)
async def save_count(
    message: Message,
    state: FSMContext,
):

    try:

        count = int(message.text)

        if count <= 0:
            raise ValueError

    except Exception:

        await message.answer(
            "Введите положительное число."
        )

        return

    CONFIG["winners_count"] = count

    save_config()

    await state.clear()

    await message.answer(
        "✅ Количество победителей обновлено."
    )


# ===============================
# РУЧНОЙ РОЗЫГРЫШ
# ===============================

@router.message(F.text == "3")
async def manual_draw(
    message: Message,
):

    if not is_admin(message.from_user.id):
        return

    participants = await db.get_all_participants()

    if not participants:

        await message.answer(
            "Нет участников."
        )

        return

    winners = choose_winners(
        participants,
        CONFIG["winners_count"],
    )

    text = "🏆 Победители:\n\n"

    for i, winner in enumerate(winners, start=1):

        username = winner.get("username")

        if username:
            text += (
                f"{i}. @{username}\n"
            )
        else:
            text += (
                f"{i}. {winner['user_id']}\n"
            )

    await message.answer(text)
