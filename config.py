"""
config.py

Загрузка настроек проекта.

Читает:

• .env
• config.json

Создает необходимые папки.

"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# =========================================================
# Пути
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

CONFIG_PATH = BASE_DIR / "config.json"

DATA_DIR = BASE_DIR / "data"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"

EXPORTS_DIR = BASE_DIR / "exports"

LOGS_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# =========================================================
# Telegram
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден в .env")

# =========================================================
# PostgreSQL
# =========================================================

DB_HOST = os.getenv("DB_HOST")

DB_PORT = int(os.getenv("DB_PORT", "5432"))

DB_NAME = os.getenv("DB_NAME")

DB_USER = os.getenv("DB_USER")

DB_PASSWORD = os.getenv("DB_PASSWORD")

required_db = [
    DB_HOST,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
]

if not all(required_db):
    raise RuntimeError(
        "Не заполнены настройки PostgreSQL в .env"
    )

# Для совместимости, если где-то используется DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

# =========================================================
# Redis (опционально)
# =========================================================

REDIS_URL = os.getenv("REDIS_URL")

# =========================================================
# S3 (опционально)
# =========================================================

USE_S3 = os.getenv(
    "USE_S3",
    "False",
).lower() == "true"

S3_ENDPOINT = os.getenv("S3_ENDPOINT")

S3_BUCKET = os.getenv("S3_BUCKET")

S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")

S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")

S3_REGION = os.getenv("S3_REGION")

# =========================================================
# Webhook (на будущее)
# =========================================================

WEBHOOK_URL = os.getenv("WEBHOOK_URL")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

# =========================================================
# Администраторы
# =========================================================

ADMIN_IDS = {
    6725848714,
    513528979,
}

# =========================================================
# Каналы для проверки подписки
# =========================================================

REQUIRED_CHANNELS = [
    {
        "id": None,
        "username": "aviasales",
        "title": "Aviasales",
    }
]

# =========================================================
# Конфиг конкурса
# =========================================================

DEFAULT_CONFIG = {

    "check_subscription": False,

    "presave_url": "",

    "start_text": "Добро пожаловать!",

    "instruction_text": (
        "Сделайте пресейв и отправьте сюда скриншот."
    ),

    "button_text": "🎵 Сделать пресейв",

    "thank_you_text": (
        "Спасибо! Вы участвуете в розыгрыше."
    ),

    "broadcast_text": "",

    "broadcast_date": "2026-12-31T20:00:00+03:00",

    "winners_count": 1,

    "auto_draw_after_broadcast": True,
}

# =========================================================
# Работа с config.json
# =========================================================


def save_config(config: dict) -> None:

    with open(
        CONFIG_PATH,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            config,
            f,
            ensure_ascii=False,
            indent=4,
        )


def load_config() -> dict:

    if not CONFIG_PATH.exists():

        save_config(DEFAULT_CONFIG)

        return DEFAULT_CONFIG.copy()

    with open(
        CONFIG_PATH,
        "r",
        encoding="utf-8",
    ) as f:

        config = json.load(f)

    changed = False

    for key, value in DEFAULT_CONFIG.items():

        if key not in config:

            config[key] = value

            changed = True

    if changed:

        save_config(config)

    return config


CONFIG = load_config()
