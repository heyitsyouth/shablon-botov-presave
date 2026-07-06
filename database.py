"""
database.py

Работа с PostgreSQL.

В этом модуле находится весь доступ к базе данных.
Никакой SQL в handlers быть не должно.
"""

from __future__ import annotations

import logging
from typing import Optional

import asyncpg

from config import DATABASE_URL

logger = logging.getLogger(__name__)


class Database:
    def __init__(self) -> None:
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        """
        Создает пул соединений.
        """

        if self.pool is not None:
            return

        self.pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=5,
            max_size=20,
            command_timeout=30,
            max_inactive_connection_lifetime=300,
        )

        logger.info("PostgreSQL pool created.")

    async def close(self) -> None:
        """
        Закрывает пул.
        """

        if self.pool:

            await self.pool.close()

            logger.info("PostgreSQL pool closed.")

    async def create_tables(self) -> None:
        """
        Создает таблицы.
        """

        async with self.pool.acquire() as conn:

            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS participants (

                    user_id BIGINT PRIMARY KEY,

                    username TEXT,

                    full_name TEXT NOT NULL,

                    screenshot_path TEXT,

                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

                );
                """
            )

            await conn.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_participants_username

                ON participants(username);
                """
            )

            await conn.execute(
                """
                CREATE INDEX IF NOT EXISTS
                idx_participants_created_at

                ON participants(created_at);
                """
            )

        logger.info("Tables checked.")

    async def participant_exists(self, user_id: int) -> bool:
        """
        Проверяет наличие участника.
        """

        async with self.pool.acquire() as conn:

            result = await conn.fetchval(
                """
                SELECT EXISTS(

                    SELECT 1

                    FROM participants

                    WHERE user_id=$1

                );
                """,
                user_id,
            )

        return bool(result)

    async def add_participant(

        self,

        user_id: int,

        username: str | None,

        full_name: str,

        screenshot_path: str,

    ) -> None:
        """
        Добавляет участника.
        """

        async with self.pool.acquire() as conn:

            await conn.execute(
                """
                INSERT INTO participants(

                    user_id,

                    username,

                    full_name,

                    screenshot_path

                )

                VALUES(

                    $1,$2,$3,$4

                )

                ON CONFLICT(user_id)

                DO UPDATE

                SET

                    username=EXCLUDED.username,

                    full_name=EXCLUDED.full_name,

                    screenshot_path=EXCLUDED.screenshot_path;
                """,
                user_id,
                username,
                full_name,
                screenshot_path,
            )

    async def get_participant(
        self,
        user_id: int,
    ) -> Optional[asyncpg.Record]:
        """
        Получить участника.
        """

        async with self.pool.acquire() as conn:

            return await conn.fetchrow(
                """
                SELECT *

                FROM participants

                WHERE user_id=$1
                """,
                user_id,
            )

    async def get_all(self) -> list[asyncpg.Record]:
        """
        Получить всех участников.
        """

        async with self.pool.acquire() as conn:

            return await conn.fetch(
                """
                SELECT *

                FROM participants

                ORDER BY created_at
                """
            )

    async def count(self) -> int:
        """
        Количество участников.
        """

        async with self.pool.acquire() as conn:

            return await conn.fetchval(
                """
                SELECT COUNT(*)

                FROM participants
                """
            )

    async def search(
        self,
        query: str,
    ) -> Optional[asyncpg.Record]:
        """
        Поиск по ID или username.
        """

        async with self.pool.acquire() as conn:

            if query.isdigit():

                return await conn.fetchrow(
                    """
                    SELECT *

                    FROM participants

                    WHERE user_id=$1
                    """,
                    int(query),
                )

            return await conn.fetchrow(
                """
                SELECT *

                FROM participants

                WHERE LOWER(username)=LOWER($1)
                """,
                query.replace("@", ""),
            )

    async def delete(
        self,
        user_id: int,
    ) -> None:
        """
        Удалить участника.
        """

        async with self.pool.acquire() as conn:

            await conn.execute(
                """
                DELETE

                FROM participants

                WHERE user_id=$1
                """,
                user_id,
            )

    async def draw_winners(
        self,
        winners_count: int,
    ) -> list[asyncpg.Record]:
        """
        Случайные победители.
        """

        async with self.pool.acquire() as conn:

            return await conn.fetch(
                """
                SELECT *

                FROM participants

                ORDER BY RANDOM()

                LIMIT $1
                """,
                winners_count,
            )

    async def statistics(self) -> dict:
        """
        Общая статистика.
        """

        async with self.pool.acquire() as conn:

            total = await conn.fetchval(
                """
                SELECT COUNT(*)

                FROM participants
                """
            )

            today = await conn.fetchval(
                """
                SELECT COUNT(*)

                FROM participants

                WHERE created_at >= CURRENT_DATE
                """
            )

        return {
            "total": total,
            "today": today,
        }


db = Database()
