"""
handlers/screenshots.py

Прием скриншотов от пользователей.
"""

from __future__ import annotations

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config import CONFIG
from database import db
from states import UserStates
from storage import storage

router = Router()


async def register_user(
    message: Message,
    state: FSMContext,
    file_id: str,
    file_unique_id: str,
):
    """
    Регистрация пользователя после получения изображения.
    """

    user = message.from_user

    if await db.participant_exists(user.id):

        await message.answer(
            "✅ Вы уже зарегистрированы в этом розыгрыше."
        )

        await state.clear()

        return

    screenshot_path = await storage.save_file(
        bot=message.bot,
        file_id=file_id,
        user_id=user.id,
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
        telegram_file_id=file_id,
        telegram_file_unique_id=file_unique_id,
    )

    await state.clear()

    await message.answer(
        CONFIG["thank_you_text"]
    )


@router.message(
    UserStates.waiting_screenshot,
    F.photo,
)
async def receive_photo(
    message: Message,
    state: FSMContext,
):

    photo = message.photo[-1]

    await register_user(
        message=message,
        state=state,
        file_id=photo.file_id,
        file_unique_id=photo.file_unique_id,
    )


@router.message(
    UserStates.waiting_screenshot,
    F.document,
)
async def receive_document(
    message: Message,
    state: FSMContext,
):

    document = message.document

    if document.mime_type is None:

        await message.answer(
            "❌ Не удалось определить тип файла."
        )

        return

    if not document.mime_type.startswith("image/"):

        await message.answer(
            "❌ Можно отправлять только изображения."
        )

        return

    await register_user(
        message=message,
        state=state,
        file_id=document.file_id,
        file_unique_id=document.file_unique_id,
    )


@router.message(UserStates.waiting_screenshot)
async def wrong_file(
    message: Message,
):

    await message.answer(
        "❌ Пришлите скриншот как фотографию или изображение."
    )
