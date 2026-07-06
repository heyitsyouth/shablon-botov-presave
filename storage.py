"""
storage.py

Сохранение изображений.

Поддерживает:

• локальное хранение
• S3 (опционально)

Возвращает путь, который затем записывается в PostgreSQL.
"""

from __future__ import annotations

import io
import logging
import uuid
from pathlib import Path

from aiogram import Bot
from PIL import Image

from config import (
    SCREENSHOTS_DIR,
    USE_S3,
    S3_BUCKET,
    S3_REGION,
    S3_ACCESS_KEY,
    S3_SECRET_KEY,
    S3_ENDPOINT,
)

logger = logging.getLogger(__name__)

try:
    from aiobotocore.session import get_session
except ImportError:
    get_session = None


class Storage:

    def __init__(self):

        self.use_s3 = USE_S3

    async def save_photo(

        self,

        bot: Bot,

        file_id: str,

    ) -> str:

        """
        Главный метод.

        Скачивает фото,
        уменьшает,
        сохраняет,
        возвращает путь.
        """

        file = await bot.get_file(file_id)

        file_bytes = await bot.download_file(file.file_path)

        image = Image.open(file_bytes)

        image = self._prepare(image)

        filename = f"{uuid.uuid4().hex}.jpg"

        if self.use_s3:

            return await self._save_s3(
                image,
                filename,
            )

        return self._save_local(
            image,
            filename,
        )

    def _prepare(
        self,
        image: Image.Image,
    ) -> Image.Image:

        """
        Подготовка изображения.

        Мы НЕ делаем сильное сжатие.

        Основная цель —
        чтобы текст оставался читаемым.
        """

        image = image.convert("RGB")

        max_size = 1800

        image.thumbnail(
            (
                max_size,
                max_size,
            )
        )

        return image

    def _save_local(

        self,

        image: Image.Image,

        filename: str,

    ) -> str:

        path = SCREENSHOTS_DIR / filename

        image.save(

            path,

            format="JPEG",

            quality=90,

            optimize=True,

        )

        logger.info(

            "Screenshot saved: %s",

            path,

        )

        return str(path)

    async def _save_s3(

        self,

        image: Image.Image,

        filename: str,

    ) -> str:

        """
        Загрузка в S3.

        Вызывается
        только если
        USE_S3=True.
        """

        if get_session is None:

            raise RuntimeError(
                "aiobotocore is not installed."
            )

        buffer = io.BytesIO()

        image.save(

            buffer,

            format="JPEG",

            quality=90,

            optimize=True,

        )

        buffer.seek(0)

        session = get_session()

        async with session.create_client(

            "s3",

            endpoint_url=S3_ENDPOINT,

            region_name=S3_REGION,

            aws_access_key_id=S3_ACCESS_KEY,

            aws_secret_access_key=S3_SECRET_KEY,

        ) as client:

            await client.put_object(

                Bucket=S3_BUCKET,

                Key=filename,

                Body=buffer.getvalue(),

                ContentType="image/jpeg",

            )

        logger.info(

            "Screenshot uploaded to S3: %s",

            filename,

        )

        return filename


storage = Storage()
