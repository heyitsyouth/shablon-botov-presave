import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

CONFIG_PATH = BASE_DIR / "config.json"

DATA_DIR = BASE_DIR / "data"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
LOGS_DIR = BASE_DIR / "logs"

DATA_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")

DATABASE_URL = os.getenv("DATABASE_URL")

REDIS_URL = os.getenv("REDIS_URL")

USE_S3 = os.getenv("USE_S3", "False").lower() == "true"

S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
S3_REGION = os.getenv("S3_REGION")

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

ADMIN_IDS = {
    6725848714,
    513528979,
}

# Пока оставляем username.
# Перед релизом заменим id на настоящий chat_id.

REQUIRED_CHANNELS = [
    {
        "id": None,
        "username": "aviasales",
        "title": "Aviasales"
    }
]

DEFAULT_CONFIG = {

    "start_text": "Добро пожаловать!",

    "instruction_text": "Сделайте пресейв и отправьте сюда скриншот.",

    "button_text": "🎵 Сделать пресейв",

    "presave_url": "",

    "thank_you_text": "Спасибо! Вы участвуете в розыгрыше.",

    "broadcast_text": "",

    "broadcast_date": "2026-07-10T20:00:00+03:00",

    "winner_count": 1,

    "auto_draw_after_broadcast": True
}


def save_config(config: dict):

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:

        json.dump(
            config,
            f,
            ensure_ascii=False,
            indent=4
        )


def load_config():

    if not CONFIG_PATH.exists():

        save_config(DEFAULT_CONFIG)

        return DEFAULT_CONFIG.copy()

    with open(CONFIG_PATH, encoding="utf-8") as f:

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
