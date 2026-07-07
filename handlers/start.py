"""
handlers/start.py

Стартовые обработчики пользователя.

Отвечает за:

• /start
• начало участия
• проверку подписки
• выдачу ссылки на пресейв
"""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from config import CONFIG
from keyboards import (
    get_start_keyboard,
    get_subscription_keyboard,
)
from states import UserStates
from utils.subscription import check_subscription

logger = logging.getLogger(__name__)

router = Router()


@router.message(F.text == "/start")
async def start(
    message: Message,
    state: FSMContext,
):
    """
    Команда /start.
    """

    await state.clear()

    text = CONFIG.get('start_text', 'Добро пожаловать!')

    await message.answer(
        text,
        reply_markup=get_start_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "send_screenshot")
async def send_screenshot_callback(
    callback: CallbackQuery,
    state: FSMContext,
):
    """
    Пользователь нажал "Отправить скриншот".
    """

    if CONFIG.get("check_subscription", False):

        ok = await check_subscription(
            callback.bot,
            callback.from_user.id,
        )

        if not ok:

            await callback.message.answer(
                "❌\n\n"
                "Сначала подпишитесь "
                "на обязательные каналы, "
                "после чего нажмите кнопку "
                "\"Я подписался\".",
                reply_markup=get_subscription_keyboard(),
            )

            await callback.answer()

            return

    await callback.message.answer(
        CONFIG.get("instruction_text", "Отправьте скриншот.")
    )

    await state.set_state(
        UserStates.waiting_screenshot
    )

    await callback.answer()


@router.callback_query(F.data == "open_presave")
async def open_presave(
    callback: CallbackQuery,
    state: FSMContext,
):
    """
    Пользователь нажал
    "Сделать пресейв".
    """

    if CONFIG.get("check_subscription", False):

        ok = await check_subscription(
            callback.bot,
            callback.from_user.id,
        )

        if not ok:

            await callback.message.answer(
                "❌\n\n"
                "Сначала подпишитесь "
                "на обязательные каналы, "
                "после чего нажмите кнопку "
                "\"Я подписался\".",
                reply_markup=get_subscription_keyboard(),
            )

            await callback.answer()

            return

    url = CONFIG.get("presave_url", "")

    if not url:

        await callback.answer(
            "Ссылка пока не настроена.",
            show_alert=True,
        )

        return

    await callback.message.answer(
        "🎵 Откройте ссылку ниже.\n\n"
        "После пресейва вернитесь "
        "в бота и отправьте "
        "скриншот.",
    )

    await callback.message.answer(
        url,
    )

    await state.set_state(
        UserStates.waiting_screenshot
    )

    await callback.answer()


@router.callback_query(F.data == "check_subscription")
async def recheck_subscription(
    callback: CallbackQuery,
    state: FSMContext,
):
    """
    Повторная проверка подписки.
    """

    ok = await check_subscription(
        callback.bot,
        callback.from_user.id,
    )

    if not ok:

        await callback.answer(
            "Подписка пока не найдена.",
            show_alert=True,
        )

        return

    url = CONFIG.get("presave_url", "")

    await callback.message.answer(
        "✅ Подписка подтверждена.\n\n"
        "Теперь сделайте пресейв "
        "по ссылке ниже, затем "
        "отправьте скриншот."
    )

    await callback.message.answer(
        url,
    )

    await state.set_state(
        UserStates.waiting_screenshot
    )

    await callback.answer()

