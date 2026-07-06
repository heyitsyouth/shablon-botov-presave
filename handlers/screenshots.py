"""
handlers/screenshots.py

Прием скриншотов от пользователей.
"""

from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import db
from storage import storage
from states import UserStates
from config import CONFIG

router = Router()


@router.message(UserStates.waiting_screenshot, F.photo)
async def receive_screenshot(
    message: Message,
    state: FSMContext,
):
    """
    Получение скриншота.
    """

    user = message.from_user

    if await db.participant_exists(user.id):

        await message.answer(
            "✅ Вы уже участвуете в этом розыгрыше."
        )

        await state.clear()

        return

    photo = message.photo[-1]

    screenshot_path = await storage.save_photo(
        bot=message.bot,
        file_id=photo.file_id,
    )

    full_name = " ".join(
        filter(
            None,
            [
                user.first_name,
                user.last_name,
            ],
        )
    )

    await db.add_participant(
        user_id=user.id,
        username=user.username,
        full_name=full_name,
        screenshot_path=screenshot_path,
        telegram_file_id=photo.file_id,
        telegram_file_unique_id=photo.file_unique_id,
    )

    await state.clear()

    await message.answer(
        CONFIG["thank_you_text"]
    )


@router.message(UserStates.waiting_screenshot)
async def not_photo(
    message: Message,
):
    """
    Если пользователь отправил не фотографию.
    """

    await message.answer(
        "❌ Пожалуйста, отправьте именно скриншот как фотографию."
    )
