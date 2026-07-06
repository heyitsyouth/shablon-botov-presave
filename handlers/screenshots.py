"""
handlers/screenshots.py
"""

from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database import db
from storage import storage
from states import UserStates
from config import CONFIG

router = Router()


async def register_user(
    message: Message,
    state: FSMContext,
    file_id: str,
    unique_id: str,
):

    user = message.from_user

    if await db.participant_exists(user.id):

        await message.answer(
            "✅ Вы уже участвуете в розыгрыше."
        )

        await state.clear()

        return

    screenshot_path = await storage.save_file(
        bot=message.bot,
        file_id=file_id,
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
        telegram_file_unique_id=unique_id,
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
        message,
        state,
        photo.file_id,
        photo.file_unique_id,
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

    if not document.mime_type:
        await message.answer(
            "Отправьте изображение."
        )
        return

    if not document.mime_type.startswith("image/"):

        await message.answer(
            "❌ Можно отправить только изображение."
        )

        return

    await register_user(
        message,
        state,
        document.file_id,
        document.file_unique_id,
    )


@router.message(UserStates.waiting_screenshot)
async def invalid_file(
    message: Message,
):

    await message.answer(
        "❌ Пришлите скриншот как фотографию или изображение."
    )
