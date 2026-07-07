"""
handlers/admin_broadcast.py

Рассылка сообщений всем участникам конкурса.
"""

from __future__ import annotations

import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from aiogram.exceptions import TelegramForbiddenError
from aiogram.exceptions import TelegramBadRequest
from aiogram.exceptions import TelegramRetryAfter

from config import CONFIG, ADMIN_IDS
from database import db
from states import AdminStates

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.callback_query(F.data == "admin_broadcast")
async def broadcast_menu(
    callback: CallbackQuery,
    state: FSMContext,
):

    if not is_admin(callback.from_user.id):
        return

    await state.set_state(
        AdminStates.waiting_broadcast_message
    )

    await callback.message.answer(
        "📣\n\n"
        "Отправьте сообщение для рассылки.\n\n"
        "Можно использовать HTML-разметку Telegram."
    )

    await callback.answer()


@router.message(AdminStates.waiting_broadcast_message)
async def process_broadcast(
    message: Message,
    state: FSMContext,
):

    if not is_admin(message.from_user.id):
        return

    users = await db.get_all_participants()

    total = len(users)

    success = 0

    failed = 0

    blocked = 0

    status = await message.answer(
        f"Начинаю рассылку...\n\n"
        f"Получателей: {total}"
    )

    for index, user in enumerate(users, start=1):

        try:

            await message.bot.send_message(
                chat_id=user["user_id"],
                text=message.html_text,
                parse_mode="HTML",
            )

            success += 1

        except TelegramForbiddenError:

            blocked += 1

        except TelegramRetryAfter as e:

            await asyncio.sleep(e.retry_after)

            try:

                await message.bot.send_message(
                    user["user_id"],
                    message.html_text,
                    parse_mode="HTML",
                )

                success += 1

            except Exception:

                failed += 1

        except TelegramBadRequest:

            failed += 1

        except Exception:

            failed += 1

        # Throttling: задержка 0.04 сек (~25 сообщений/сек), чтобы избежать банов и лимитов Telegram API
        await asyncio.sleep(0.04)

        if index % 100 == 0:

            await status.edit_text(

                f"📣 Рассылка...\n\n"

                f"{index}/{total}\n\n"

                f"✅ {success}\n"

                f"❌ {failed}\n"

                f"🚫 {blocked}"
            )

            await asyncio.sleep(0.05)

    await status.edit_text(

        "✅ Рассылка завершена.\n\n"

        f"Получателей: {total}\n\n"

        f"✅ Успешно: {success}\n"

        f"❌ Ошибки: {failed}\n"

        f"🚫 Заблокировали бота: {blocked}"

    )


    await state.clear()
