"""
handlers/admin_export.py

Экспорт участников конкурса в CSV.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile

from config import ADMIN_IDS
from utils.export_csv import export_participants

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.callback_query(F.data == "admin_export_csv")
async def export_csv(callback: CallbackQuery):

    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа.", show_alert=True)
        return

    await callback.answer("Подготавливаю CSV...")

    file_path = await export_participants()

    await callback.message.answer_document(
        document=FSInputFile(file_path),
        caption="📥 Экспорт участников конкурса"
    )
