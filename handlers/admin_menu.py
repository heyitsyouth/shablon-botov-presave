"""
handlers/admin_menu.py

Главное меню администратора.
"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

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


@router.callback_query(F.data == "admin_stats")
async def admin_stats_callback(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        return

    stats = await db.statistics()

    text = (
        "⚙️ <b>Панель администратора</b>\n\n"
        f"👥 Всего участников: <b>{stats['total']}</b>\n"
        f"📅 Сегодня: <b>{stats['today']}</b>\n\n"
        "Выберите действие:"
    )

    try:
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_admin_keyboard(),
        )
    except Exception:
        pass

    await callback.answer("Статистика обновлена.")


@router.callback_query(F.data == "admin_toggle_sub")
async def admin_toggle_sub_callback(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        return

    from config import save_config, CONFIG

    check_sub = not CONFIG.get("check_subscription", False)

    CONFIG["check_subscription"] = check_sub

    save_config(CONFIG)

    try:
        await callback.message.edit_reply_markup(
            reply_markup=get_admin_keyboard()
        )
    except Exception:
        pass

    status_msg = "ВКЛЮЧЕНА" if check_sub else "ВЫКЛЮЧЕНА"

    await callback.answer(
        f"Проверка подписки {status_msg}.",
        show_alert=True,
    )


