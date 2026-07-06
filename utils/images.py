"""
images.py

Вся обработка изображений.

Модуль ничего не знает
про Telegram,
PostgreSQL
или S3.

Он умеет только работать
с изображениями.
"""

from __future__ import annotations

from io import BytesIO

from PIL import Image, ImageOps


MAX_IMAGE_SIZE = 1800

JPEG_QUALITY = 90


def prepare_image(file_bytes: BytesIO) -> Image.Image:
    """
    Подготовка изображения.

    - исправление EXIF-поворота
    - RGB
    - уменьшение
    """

    image = Image.open(file_bytes)

    image = ImageOps.exif_transpose(image)

    image = image.convert("RGB")

    image.thumbnail(
        (
            MAX_IMAGE_SIZE,
            MAX_IMAGE_SIZE,
        )
    )

    return image


def image_to_bytes(image: Image.Image) -> BytesIO:
    """
    Конвертация изображения
    в BytesIO.
    """

    buffer = BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=JPEG_QUALITY,
        optimize=True,
    )

    buffer.seek(0)

    return buffer
