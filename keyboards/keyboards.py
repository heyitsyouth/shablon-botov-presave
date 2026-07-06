"""
Все клавиатуры бота.

Никакой логики здесь быть не должно —
только создание клавиатур.
"""

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from config import CONFIG


def get_start_keyboard() -> InlineKeyboardMarkup:
    """
    Главное меню пользователя.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=CONFIG["button_text"],
                    callback_data="open_presave",
                )
            ]
        ]
    )


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура проверки подписки.

    Используется только если
    check_subscription=True.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Я подписался",
                    callback_data="check_subscription",
                )
            ]
        ]
    )


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """
    Кнопка отмены.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="cancel",
                )
            ]
        ]
    )


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """
    Главное меню администратора.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📊 Статистика",
                    callback_data="admin_stats",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 Изменить тексты",
                    callback_data="admin_texts",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📅 Дата розыгрыша",
                    callback_data="admin_draw_date",
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Победители",
                    callback_data="admin_draw",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📣 Рассылка",
                    callback_data="admin_broadcast",
                )
            ],
        ]
    )
