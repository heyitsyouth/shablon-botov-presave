"""
handlers/screenshots.py

Приём скриншотов пользователя.
"""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import CONFIG
from database import db
from states import UserStates
from storage import storage

logger = logging.getLogger(__name__)

router = Router()


@router.message(UserStates.waiting_for_screenshot, F.photo)
async def receive_screenshot(
    message: Message,
    state: FSMContext,
):
    """
    Получение скриншота.
    """

    if await db.participant_exists(message.from_user.id):

        await message.answer(
            "Вы уже зарегистрированы "
            "в розыгрыше."
        )

        await state.clear()

        return

    photo = message.photo[-1]

    path = await storage.save_photo(
        message.bot,
        photo.file_id,
    )

    username = message.from_user.username

    full_name = message.from_user.full_name

    await db.add_participant(
    user_id=message.from_user.id,
    username=username,
    full_name=full_name,
    screenshot_path=path,
    )

    logger.info(
        "New participant: %s",
        message.from_user.id,
    )

    await message.answer(
        CONFIG["thank_you_text"]
    )

    await state.clear()


@router.message(UserStates.waiting_for_screenshot)
async def wrong_message(
    message: Message,
):
    """
    Пользователь отправил
    не фотографию.
    """

    await message.answer(
        "Пожалуйста, отправьте "
        "именно фотографию "
        "со скриншотом пресейва."
    )
