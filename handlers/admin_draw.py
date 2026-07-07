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

from config import CONFIG, ADMIN_IDS, save_config
from database import db
from states import AdminStates
from utils.draw import choose_winners
from keyboards import get_draw_menu_keyboard, get_cancel_keyboard, get_admin_keyboard

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ===============================
# Меню розыгрыша
# ===============================

@router.callback_query(F.data == "admin_draw")
async def draw_menu(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        return

    # Красиво форматируем вывод даты для админа
    raw_date = CONFIG.get('broadcast_date', '')
    formatted_date = "Не задана"
    if raw_date:
        try:
            dt = datetime.fromisoformat(raw_date)
            formatted_date = dt.strftime("%d.%m.%Y %H:%M (МСК/UTC+3)")
        except ValueError:
            formatted_date = raw_date

    text = (
        "🎲 <b>Настройки розыгрыша</b>\n\n"
        f"📅 <b>Текущая дата розыгрыша:</b> {formatted_date}\n"
        f"🏆 <b>Количество победителей:</b> {CONFIG['winners_count']}\n\n"
        "Что вы хотите настроить?"
    )

    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_draw_menu_keyboard()
    )

    await callback.answer()


# ===============================
# ДАТА
# ===============================

@router.callback_query(F.data == "admin_draw_edit_date_start")
async def edit_date_start(
    callback: CallbackQuery,
    state: FSMContext,
):
    if not is_admin(callback.from_user.id):
        return

    await state.set_state(
        AdminStates.waiting_broadcast_date
    )

    await callback.message.answer(
        "📝 <b>Введите новую дату и время розыгрыша</b>\n\n"
        "Вы можете написать дату в любом удобном формате:\n"
        "• <code>ДД.ММ.ГГГГ ЧЧ:ММ</code> (например: <code>31.12.2026 20:00</code>)\n"
        "• <code>ДД.ММ ЧЧ:ММ</code> (например: <code>31.12 15:30</code> — текущий год подставится автоматически)\n"
        "• ISO-формат: <code>2026-12-31T20:00:00+03:00</code>",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@router.message(AdminStates.waiting_broadcast_date)
async def save_date(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    date_str = message.text.strip()
    parsed_date = None

    # 1. ДД.ММ.ГГГГ ЧЧ:ММ (31.12.2026 20:00)
    try:
        parsed_date = datetime.strptime(date_str, "%d.%m.%Y %H:%M")
    except ValueError:
        pass

    # 2. ДД.ММ.ГГ ЧЧ:ММ (31.12.26 20:00)
    if not parsed_date:
        try:
            parsed_date = datetime.strptime(date_str, "%d.%m.%y %H:%M")
        except ValueError:
            pass

    # 3. ДД.ММ ЧЧ:ММ (31.12 20:00) - текущий год
    if not parsed_date:
        try:
            parsed_date = datetime.strptime(date_str, "%d.%m %H:%M")
            parsed_date = parsed_date.replace(year=datetime.now().year)
        except ValueError:
            pass

    if parsed_date:
        # Устанавливаем часовой пояс +03:00 (МСК) по умолчанию
        iso_str = f"{parsed_date.strftime('%Y-%m-%dT%H:%M')}:00+03:00"
    else:
        # Пытаемся спарсить ISO формат
        try:
            datetime.fromisoformat(date_str)
            iso_str = date_str
        except ValueError:
            await message.answer(
                "❌ <b>Неверный формат даты.</b>\n\n"
                "Пожалуйста, введите дату в одном из следующих форматов:\n"
                "• <code>ДД.ММ.ГГГГ ЧЧ:ММ</code> (например: <code>31.12.2026 20:00</code>)\n"
                "• <code>ДД.ММ ЧЧ:ММ</code> (например: <code>31.12 20:00</code>)\n"
                "• ISO-формат: <code>2026-12-31T20:00:00+03:00</code>",
                parse_mode="HTML",
                reply_markup=get_cancel_keyboard()
            )
            return

    CONFIG["broadcast_date"] = iso_str
    save_config(CONFIG)

    await state.clear()

    # Форматируем для подтверждения
    dt = datetime.fromisoformat(iso_str)
    user_friendly_date = dt.strftime("%d.%m.%Y %H:%M (МСК)")

    await message.answer(
        f"✅ <b>Дата успешно сохранена!</b>\n"
        f"Установленное время: {user_friendly_date}",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )


# ===============================
# КОЛИЧЕСТВО ПОБЕДИТЕЛЕЙ
# ===============================

@router.callback_query(F.data == "admin_draw_edit_count_start")
async def edit_count_start(
    callback: CallbackQuery,
    state: FSMContext,
):
    if not is_admin(callback.from_user.id):
        return

    await state.set_state(
        AdminStates.waiting_winners_count
    )

    await callback.message.answer(
        "🏆 <b>Введите желаемое количество победителей:</b>\n\n"
        "Отправьте боту число (например, <code>5</code>)",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()


@router.message(AdminStates.waiting_winners_count)
async def save_count(
    message: Message,
    state: FSMContext,
):
    if not is_admin(message.from_user.id):
        return

    try:
        count = int(message.text)
        if count <= 0:
            raise ValueError
    except Exception:
        await message.answer(
            "❌ <b>Пожалуйста, введите положительное целое число.</b>",
            parse_mode="HTML",
            reply_markup=get_cancel_keyboard()
        )
        return

    CONFIG["winners_count"] = count
    save_config(CONFIG)

    await state.clear()

    await message.answer(
        f"✅ <b>Количество победителей обновлено: {count}</b>",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )


# ===============================
# РУЧНОЙ РОЗЫГРЫШ
# ===============================

@router.callback_query(F.data == "admin_draw_now_confirm")
async def manual_draw(
    callback: CallbackQuery,
):
    if not is_admin(callback.from_user.id):
        return

    participants = await db.get_all_participants()

    if not participants:
        await callback.message.answer(
            "❌ <b>Ошибка:</b> нет зарегистрированных участников для проведения розыгрыша.",
            parse_mode="HTML",
            reply_markup=get_admin_keyboard()
        )
        await callback.answer()
        return

    winners = choose_winners(
        participants,
        CONFIG["winners_count"],
    )

    text = (
        f"🎲 <b>Результаты ручного розыгрыша:</b>\n\n"
        f"Всего участников: <b>{len(participants)}</b>\n"
        f"Выбрано победителей: <b>{len(winners)}</b> из <b>{CONFIG['winners_count']}</b> запланированных\n\n"
        f"🏆 <b>Победители:</b>\n"
    )

    for i, winner in enumerate(winners, start=1):
        username = winner.get("username")
        if username:
            text += f"{i}. @{username} (ID: <code>{winner['user_id']}</code>)\n"
        else:
            text += f"{i}. {winner['full_name']} (ID: <code>{winner['user_id']}</code>)\n"

    await callback.message.answer(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()
