"""
keyboards/keyboards.py

Все клавиатуры проекта.
"""

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def get_start_keyboard(url: str) -> InlineKeyboardMarkup:
    """
    Главное меню пользователя.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎵 Сделать пресейв",
                    url=url,
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Отправить скриншот",
                    callback_data="send_screenshot",
                )
            ],
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
                ),
                InlineKeyboardButton(
                    text="🎲 Розыгрыш",
                    callback_data="admin_draw",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📝 Тексты",
                    callback_data="admin_texts",
                ),
                InlineKeyboardButton(
                    text="📣 Рассылка",
                    callback_data="admin_broadcast",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📥 Скачать CSV",
                    callback_data="admin_export_csv",
                )
            ],
        ]
    )
