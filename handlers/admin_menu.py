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


@router.callback_query(F.data == "admin_view_config")
async def admin_view_config_callback(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        return

    from config import CONFIG

    check_sub = CONFIG.get("check_subscription", False)

    status_sub = "🟢 ВКЛЮЧЕНА" if check_sub else "🔴 ВЫКЛЮЧЕНА"

    text = (
        "📋 <b>Текущие настройки розыгрыша:</b>\n\n"
        f"🔗 <b>Пресейв-ссылка:</b>\n<code>{CONFIG.get('presave_url', 'Не задана')}</code>\n\n"
        f"📢 <b>Обязательный канал:</b>\n"
        f"Название: <b>{CONFIG.get('channel_title', 'Не задано')}</b>\n"
        f"Юзернейм: @{CONFIG.get('channel_username', 'Не задан')}\n"
        f"Статус проверки: <b>{status_sub}</b>\n\n"
        f"📝 <b>Стартовый текст:</b>\n{CONFIG.get('start_text', 'Не задан')}\n\n"
        f"ℹ️ <b>Инструкция:</b>\n{CONFIG.get('instruction_text', 'Не задана')}\n\n"
        f"💖 <b>Текст благодарности:</b>\n{CONFIG.get('thank_you_text', 'Не задан')}\n\n"
        f"💬 <b>Текст рассылки:</b>\n{CONFIG.get('broadcast_text', 'Не задан')}\n\n"
        f"📅 <b>Дата авто-розыгрыша:</b>\n{CONFIG.get('broadcast_date', 'Не задана')}\n"
        f"🏆 <b>Количество победителей:</b> {CONFIG.get('winners_count', 1)}"
    )

    await callback.message.answer(
        text,
        parse_mode="HTML",
    )

    await callback.answer()



