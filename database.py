"""
database.py

Работа с PostgreSQL.
"""

from __future__ import annotations

import asyncpg

from config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
)


class Database:

    def __init__(self):

        self.pool = None

    # ----------------------------------------
    # Подключение
    # ----------------------------------------

    async def connect(self):

        self.pool = await asyncpg.create_pool(

            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,

            min_size=1,
            max_size=10,

        )

        await self.create_tables()

    async def close(self):

        if self.pool:
            await self.pool.close()

    # ----------------------------------------
    # Создание таблиц
    # ----------------------------------------

    async def create_tables(self):

        async with self.pool.acquire() as conn:

            await conn.execute("""

            CREATE TABLE IF NOT EXISTS participants (

                id SERIAL PRIMARY KEY,

                user_id BIGINT UNIQUE NOT NULL,

                username TEXT,

                full_name TEXT,

                screenshot_path TEXT NOT NULL,

                telegram_file_id TEXT NOT NULL,

                telegram_file_unique_id TEXT NOT NULL,

                created_at TIMESTAMP NOT NULL DEFAULT NOW()

            );

            """)

    # ----------------------------------------
    # Вспомогательные методы
    # ----------------------------------------

    async def execute(
        self,
        query: str,
        *args,
    ):

        async with self.pool.acquire() as conn:

            return await conn.execute(
                query,
                *args,
            )

    async def fetch(
        self,
        query: str,
        *args,
    ):

        async with self.pool.acquire() as conn:

            return await conn.fetch(
                query,
                *args,
            )

    async def fetchrow(
        self,
        query: str,
        *args,
    ):

        async with self.pool.acquire() as conn:

            return await conn.fetchrow(
                query,
                *args,
            )

    async def fetchval(
        self,
        query: str,
        *args,
    ):

        async with self.pool.acquire() as conn:

            return await conn.fetchval(
                query,
                *args,
            )

    # ----------------------------------------
    # Участники
    # ----------------------------------------

    async def participant_exists(
        self,
        user_id: int,
    ) -> bool:

        result = await self.fetchval(
            """
            SELECT EXISTS(
                SELECT 1
                FROM participants
                WHERE user_id = $1
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
        telegram_file_id: str,
        telegram_file_unique_id: str,
    ):

        await self.execute(
            """
            INSERT INTO participants (

                user_id,
                username,
                full_name,
                screenshot_path,
                telegram_file_id,
                telegram_file_unique_id

            )

            VALUES (

                $1,
                $2,
                $3,
                $4,
                $5,
                $6

            )

            ON CONFLICT (user_id)
            DO NOTHING;
            """,
            user_id,
            username,
            full_name,
            screenshot_path,
            telegram_file_id,
            telegram_file_unique_id,
        )

    async def get_participant(
        self,
        user_id: int,
    ):

        row = await self.fetchrow(
            """
            SELECT *
            FROM participants
            WHERE user_id = $1;
            """,
            user_id,
        )

        if row is None:
            return None

        return dict(row)

    async def get_all_participants(self):

        rows = await self.fetch(
            """
            SELECT *
            FROM participants
            ORDER BY created_at ASC;
            """
        )

        return [dict(row) for row in rows]

    async def statistics(self):

        total = await self.fetchval(
            """
            SELECT COUNT(*)
            FROM participants;
            """
        )

        today = await self.fetchval(
            """
            SELECT COUNT(*)
            FROM participants
            WHERE DATE(created_at) = CURRENT_DATE;
            """
        )

        return {
            "total": total,
            "today": today,
        }

    async def delete_participant(
        self,
        user_id: int,
    ):

        await self.execute(
            """
            DELETE FROM participants
            WHERE user_id = $1;
            """,
            user_id,
        )

    async def clear_participants(self):

        await self.execute(
            """
            TRUNCATE TABLE participants
            RESTART IDENTITY;
            """
        )

    async def random_winners(
        self,
        count: int,
    ):

        rows = await self.fetch(
            """
            SELECT *
            FROM participants
            ORDER BY RANDOM()
            LIMIT $1;
            """,
            count,
        )

        return [dict(row) for row in rows]
        
db = Database()
