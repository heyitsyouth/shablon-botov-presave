"""
keyboards.py

Все клавиатуры проекта.
"""

from __future__ import annotations

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import CONFIG


# =========================================================
# Пользователь
# =========================================================

def get_start_keyboard() -> InlineKeyboardMarkup:

    keyboard = [
        [
            InlineKeyboardButton(
                text=CONFIG["button_text"],
                url=CONFIG["presave_url"],
            )
        ],
        [
            InlineKeyboardButton(
                text="📤 Отправить скриншот",
                callback_data="send_screenshot",
            )
        ]
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


# =========================================================
# Админ
# =========================================================

def get_admin_keyboard() -> InlineKeyboardMarkup:

    keyboard = [

        [
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="admin_stats",
            )
        ],

        [
            InlineKeyboardButton(
                text="📝 Тексты",
                callback_data="admin_texts",
            )
        ],

        [
            InlineKeyboardButton(
                text="🎲 Розыгрыш",
                callback_data="admin_draw",
            )
        ],

        [
            InlineKeyboardButton(
                text="📣 Рассылка",
                callback_data="admin_broadcast",
            )
        ],

        [
            InlineKeyboardButton(
                text="📥 Скачать CSV",
                callback_data="admin_export_csv",
            )
        ],

    ]

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def get_cancel_keyboard() -> InlineKeyboardMarkup:

    keyboard = [
        [
            InlineKeyboardButton(
                text="❌ Отменить",
                callback_data="cancel",
            )
        ]
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


def get_subscription_keyboard() -> InlineKeyboardMarkup:

    from config import REQUIRED_CHANNELS

    keyboard = []

    for channel in REQUIRED_CHANNELS:

        username = channel.get("username")

        title = channel.get("title", "Канал")

        if username:

            keyboard.append([
                InlineKeyboardButton(
                    text=f"Подписаться на {title}",
                    url=f"https://t.me/{username}",
                )
            ])

    keyboard.append([
        InlineKeyboardButton(
            text="Я подписался",
            callback_data="check_subscription",
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )

