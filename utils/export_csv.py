"""
utils/export_csv.py

Экспорт участников конкурса в CSV.
"""

from __future__ import annotations

import csv
from pathlib import Path

from database import db


EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)


async def export_participants() -> Path:
    """
    Экспортирует всех участников конкурса в CSV.

    Возвращает путь к готовому файлу.
    """

    participants = await db.get_all_participants()

    file_path = EXPORT_DIR / "participants.csv"

    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow(
            [
                "user_id",
                "username",
                "full_name",
                "created_at",
                "screenshot_path",
                "telegram_file_id",
                "telegram_file_unique_id",
            ]
        )

        for participant in participants:

            writer.writerow(
                [
                    participant["user_id"],
                    participant["username"] or "",
                    participant["full_name"] or "",
                    participant["created_at"],
                    participant["screenshot_path"],
                    participant["telegram_file_id"],
                    participant["telegram_file_unique_id"],
                ]
            )

    return file_path
