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

from datetime import datetime
from pathlib import Path

from aiogram import Bot
from PIL import Image, ImageOps

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

    async def save_file(
        self,
        bot: Bot,
        file_id: str,
        user_id: int,
    ) -> str:
        """
        Сохраняет изображение пользователя.
        """

        telegram_file = await bot.get_file(file_id)

        file_bytes = await bot.download_file(
            telegram_file.file_path
        )

        image = Image.open(file_bytes)

        image = self._prepare(image)

        now = datetime.now()

        folder = (
            SCREENSHOTS_DIR
            / f"{now:%Y}"
            / f"{now:%m}"
            / f"{now:%d}"
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = (
            f"{user_id}_"
            f"{now:%Y%m%d_%H%M%S}.jpg"
        )

        if self.use_s3:

            return await self._save_s3(
                image,
                filename,
            )

        return self._save_local(
            image,
            folder,
            filename,
        )

    async def save_photo(
        self,
        bot: Bot,
        file_id: str,
        user_id: int,
    ) -> str:

        return await self.save_file(
            bot,
            file_id,
            user_id,
        )

    def _prepare(
        self,
        image: Image.Image,
    ) -> Image.Image:

        image = ImageOps.exif_transpose(image)

        image = image.convert("RGB")

        image.thumbnail(
            (
                1800,
                1800,
            )
        )

        return image

    def _save_local(
        self,
        image: Image.Image,
        folder: Path,
        filename: str,
    ) -> str:

        path = folder / filename

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
