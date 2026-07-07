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

    presave_url = CONFIG.get("presave_url", "")

    keyboard = []

    if presave_url.strip():

        keyboard.append([
            InlineKeyboardButton(
                text=CONFIG.get("button_text", "🎵 Сделать пресейв"),
                url=presave_url,
            )
        ])

    else:

        keyboard.append([
            InlineKeyboardButton(
                text=CONFIG.get("button_text", "🎵 Сделать пресейв"),
                callback_data="open_presave",
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            text="📤 Отправить скриншот",
            callback_data="send_screenshot",
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )



# =========================================================
# Админ
# =========================================================

def get_admin_keyboard() -> InlineKeyboardMarkup:

    check_sub = CONFIG.get("check_subscription", False)

    status_text = "🔔 Подписка: ВКЛ" if check_sub else "🔕 Подписка: ВЫКЛ"

    keyboard = [

        [
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="admin_stats",
            )
        ],

        [
            InlineKeyboardButton(
                text="📋 Просмотр настроек",
                callback_data="admin_view_config",
            )
        ],

        [
            InlineKeyboardButton(
                text=status_text,
                callback_data="admin_toggle_sub",
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

    username = CONFIG.get("channel_username", "aviasales")

    title = CONFIG.get("channel_title", "Aviasales")

    keyboard = []

    if username:

        keyboard.append([
            InlineKeyboardButton(
                text=f"Подписаться на {title}",
                url=f"https://t.me/{username.replace('@', '').strip()}",
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


