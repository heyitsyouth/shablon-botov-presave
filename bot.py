import asyncio
import os
import random
import json
from datetime import datetime, timezone, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан")

ADMIN_IDS = [513528979]   # замените на свои ID

DATA_DIR = "data"
SCREENSHOT_DIR = os.path.join(DATA_DIR, "screenshots")
PARTICIPANTS_FILE = os.path.join(DATA_DIR, "participants.txt")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
if not os.path.exists(PARTICIPANTS_FILE):
    open(PARTICIPANTS_FILE, 'w', encoding='utf-8').close()

# Загрузка/создание конфигурации
DEFAULT_CONFIG = {
    "start_text": "привет! ты на пути к крутому призу за то, что ты крутой, а еще в честь релиза «».\n\n🎁 за пресейв ты участвуешь в розыгрыше",
    "button_text": "✅ сделать пресейв и получить награды",
    "instruction_text": "1️⃣ сделай пресейв по ссылке  (нужно отключить VPN!)\n2️⃣ как сделал:а, отправь скриншот, где видно, что пресейвы есть\n\nжду скриншот следующим сообщением: после этого ты будешь участвовать в розыгрыше!",
    "thank_you_text": "ты участвуешь в розыгрыше",
    "broadcast_text": "ТРЕК \"\" УЖЕ В СЕТИ!\nпослушать: ",
    "broadcast_date": "",
    "winners_count": 1
}

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)

def load_config():
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

# Переменные для кэша (необязательно)
config = load_config()

# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
def get_broadcast_datetime():
    dt = datetime.fromisoformat(config["broadcast_date"])
    # если нет часового пояса, назначаем UTC+3
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone(timedelta(hours=3)))
    return dt

def find_participant(query: str):
    with open(PARTICIPANTS_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) < 4:
                continue
            uid, name, uname, fname = parts[0], parts[1], parts[2], parts[3]
            if query.isdigit() and uid == query:
                return (uid, name, uname, fname)
            clean_query = query.lstrip('@').lower()
            if uname.lower() == clean_query:
                return (uid, name, uname, fname)
    return None

# ========== КЛАВИАТУРЫ ==========
def get_main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=config["button_text"])]],
        resize_keyboard=True
    )

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📋 Список участников")],
        [KeyboardButton(text="🎲 Розыгрыш")],
        [KeyboardButton(text="🔍 Проверить участника")],
        [KeyboardButton(text="⏳ Время до рассылки")],
        [KeyboardButton(text="⚙️ Настройки")],
        [KeyboardButton(text="❌ Скрыть меню")]
    ],
    resize_keyboard=True
)

# ========== FSM ==========
class PresaveState(StatesGroup):
    waiting_screenshot = State()

class AdminCheckState(StatesGroup):
    waiting_user_id = State()

class AdminSetTextState(StatesGroup):
    waiting_field = State()
    waiting_value = State()

# ========== ФУНКЦИЯ РАССЫЛКИ ==========
async def send_broadcast():
    broadcast_sent_file = os.path.join(DATA_DIR, "broadcast_sent.txt")
    if not os.path.exists(broadcast_sent_file):
        with open(broadcast_sent_file, 'w', encoding='utf-8') as f:
            f.write("False")
    with open(broadcast_sent_file, 'r', encoding='utf-8') as f:
        sent = f.read().strip()
    if sent == "True":
        print("Рассылка уже была отправлена ранее.")
        return

    with open(PARTICIPANTS_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if not lines:
        print("Нет участников для рассылки.")
        return

    count = 0
    for line in lines:
        parts = line.strip().split('|')
        if len(parts) >= 1:
            user_id = int(parts[0])
            try:
                await bot.send_message(user_id, config["broadcast_text"])
                count += 1
                await asyncio.sleep(0.3)
            except Exception as e:
                print(f"Не удалось отправить {user_id}: {e}")

    with open(broadcast_sent_file, 'w', encoding='utf-8') as f:
        f.write("True")
    print(f"Рассылка завершена. Отправлено {count} сообщений.")

async def schedule_broadcast():
    target = get_broadcast_datetime()
    now = datetime.now(timezone(timedelta(hours=3)))
    if now >= target:
        broadcast_sent_file = os.path.join(DATA_DIR, "broadcast_sent.txt")
        if os.path.exists(broadcast_sent_file):
            with open(broadcast_sent_file, 'r', encoding='utf-8') as f:
                sent = f.read().strip()
        else:
            sent = "False"
        if sent != "True":
            await send_broadcast()
    else:
        wait_seconds = (target - now).total_seconds()
        print(f"До рассылки {wait_seconds} секунд. Ожидание...")
        await asyncio.sleep(wait_seconds)
        await send_broadcast()

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ========== ОБЩИЕ КОМАНДЫ ==========
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(config["start_text"], reply_markup=get_main_kb())

@dp.message(F.text == config["button_text"])
async def ask_screenshot(message: types.Message, state: FSMContext):
    await state.set_state(PresaveState.waiting_screenshot)
    await message.answer(config["instruction_text"], reply_markup=ReplyKeyboardRemove())

@dp.message(PresaveState.waiting_screenshot, F.photo)
async def save_screenshot(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username or "no_username"

    already_exists = False
    if os.path.exists(PARTICIPANTS_FILE):
        with open(PARTICIPANTS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) > 0 and parts[0] == str(user_id):
                    already_exists = True
                    break

    if already_exists:
        await message.answer("Вы уже участвуете в розыгрыше! Спасибо за поддержку ❤️")
        await state.clear()
        return

    photo = message.photo[-1]
    file = await bot.get_file(photo.file_id)
    ext = file.file_path.split('.')[-1] if '.' in file.file_path else 'jpg'
    filename = f"{user_id}_{int(message.date.timestamp())}.{ext}"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    await bot.download_file(file.file_path, filepath)

    with open(PARTICIPANTS_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{user_id}|{full_name}|{username}|{filename}\n")

    await message.answer(config["thank_you_text"])
    await state.clear()

@dp.message(PresaveState.waiting_screenshot)
async def wrong_input(message: types.Message):
    await message.answer("пожалуйста, отправь именно скриншот (фото)")

# ========== АДМИН-ПАНЕЛЬ ==========
@dp.message(Command("admin"))
async def admin_panel(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    await state.clear()
    await message.answer("Админ-панель. Выберите действие:", reply_markup=admin_kb)

@dp.message(F.text == "📋 Список участников")
async def admin_participants(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    with open(PARTICIPANTS_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if not lines:
        await message.answer("пока нет участников")
        return
    header = f"📋 Всего участников: {len(lines)}\n\nСписок:\n"
    body = ""
    for line in lines:
        parts = line.strip().split('|')
        if len(parts) >= 3:
            uid, name, uname = parts[0], parts[1], parts[2]
            body += f"👤 {name} (@{uname}) – ID {uid}\n"
    await message.answer(header + body)

@dp.message(F.text == "🎲 Розыгрыш")
async def admin_draw(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    with open(PARTICIPANTS_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if not lines:
        await message.answer("нет участников для розыгрыша")
        return
    winners_count = config.get("winners_count", 1)
    if winners_count > len(lines):
        winners_count = len(lines)
    winners = random.sample(lines, winners_count)
    result_text = f"🎉 РОЗЫГРЫШ 🎉\n\nПобедители ({len(winners)}):\n"
    for idx, w in enumerate(winners, 1):
        parts = w.strip().split('|')
        if len(parts) >= 3:
            uid, name, uname = parts[0], parts[1], parts[2]
            result_text += f"{idx}. {name} (@{uname}) – ID {uid}\n"
    await message.answer(result_text)
    # Отправляем скриншоты победителей (по желанию, можно отключить)
    for w in winners:
        parts = w.strip().split('|')
        if len(parts) >= 4:
            uid, name, uname, filename = parts[0], parts[1], parts[2], parts[3]
            path = os.path.join(SCREENSHOT_DIR, filename)
            if os.path.exists(path):
                await message.answer_photo(FSInputFile(path), caption=f"{name} (@{uname})")
            else:
                await message.answer(f"⚠️ Скриншот {name} не найден ({filename})")
        await asyncio.sleep(0.5)

@dp.message(F.text == "🔍 Проверить участника")
async def admin_check_start(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    await state.set_state(AdminCheckState.waiting_user_id)
    await message.answer(
        "Введите ID пользователя (число) или @username (можно без @):",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(AdminCheckState.waiting_user_id)
async def admin_check_user(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await state.clear()
        await message.answer("нет прав ))")
        return
    query = message.text.strip()
    found = find_participant(query)
    if not found:
        await message.answer("участник с таким ID или username не найден")
        await state.clear()
        await message.answer("Вернуться в админ-панель: /admin", reply_markup=ReplyKeyboardRemove())
        return
    uid, full_name, username, filename = found
    screenshot_path = os.path.join(SCREENSHOT_DIR, filename)
    caption = f"скриншот участника {full_name} (@{username}) (ID {uid}):"
    if os.path.exists(screenshot_path):
        await message.answer_photo(FSInputFile(screenshot_path), caption=caption)
    else:
        await message.answer(f"{caption}\n⚠️ файл скриншота не найден")
    await state.clear()
    await message.answer("Готово. Для продолжения используйте /admin или кнопки.", reply_markup=admin_kb)

@dp.message(F.text == "⏳ Время до рассылки")
async def admin_time_to_broadcast(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    target = get_broadcast_datetime()
    now = datetime.now(timezone(timedelta(hours=3)))
    if now >= target:
        await message.answer("⏰ Время рассылки уже наступило или прошло. Если рассылка ещё не была отправлена, она запустится автоматически при следующей проверке.")
    else:
        delta = target - now
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        await message.answer(f"⏳ До автоматической рассылки осталось:\n{days} дн. {hours} ч. {minutes} мин. {seconds} сек.")

@dp.message(F.text == "⚙️ Настройки")
async def admin_settings(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    settings_text = (
        "⚙️ *Текущие настройки:*\n\n"
        f"📌 *Текст приветствия*: {config['start_text'][:100]}...\n"
        f"🔘 *Текст кнопки*: {config['button_text']}\n"
        f"📖 *Текст инструкции*: {config['instruction_text'][:100]}...\n"
        f"🎁 *Текст благодарности*: {config['thank_you_text'][:100]}...\n"
        f"📢 *Текст рассылки*: {config['broadcast_text'][:100]}...\n"
        f"📅 *Дата рассылки*: {config['broadcast_date']}\n"
        f"🏆 *Количество победителей*: {config['winners_count']}\n\n"
        "Изменить параметры можно командами:\n"
        "/set_start_text <текст>\n"
        "/set_button_text <текст>\n"
        "/set_instruction_text <текст>\n"
        "/set_thank_you_text <текст>\n"
        "/set_broadcast_text <текст>\n"
        "/set_broadcast_date ГГГГ-ММ-ДДTЧЧ:ММ:СС+03:00\n"
        "/set_winners <число>"
    )
    await message.answer(settings_text, parse_mode="Markdown")

# Команды для изменения настроек
@dp.message(Command("set_start_text"))
async def set_start_text(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    new_text = message.text.replace("/set_start_text", "").strip()
    if not new_text:
        await message.answer("Укажите текст после команды.")
        return
    config["start_text"] = new_text
    save_config(config)
    await message.answer("✅ Текст приветствия обновлён.")

@dp.message(Command("set_button_text"))
async def set_button_text(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    new_text = message.text.replace("/set_button_text", "").strip()
    if not new_text:
        await message.answer("Укажите текст после команды.")
        return
    config["button_text"] = new_text
    save_config(config)
    # Обновляем клавиатуру (но она обновится только при новом старте или при следующем вызове start)
    await message.answer("✅ Текст кнопки обновлён. Для обновления клавиатуры перезапустите бота или используйте /start.")

@dp.message(Command("set_instruction_text"))
async def set_instruction_text(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    new_text = message.text.replace("/set_instruction_text", "").strip()
    if not new_text:
        await message.answer("Укажите текст после команды.")
        return
    config["instruction_text"] = new_text
    save_config(config)
    await message.answer("✅ Текст инструкции обновлён.")

@dp.message(Command("set_thank_you_text"))
async def set_thank_you_text(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    new_text = message.text.replace("/set_thank_you_text", "").strip()
    if not new_text:
        await message.answer("Укажите текст после команды.")
        return
    config["thank_you_text"] = new_text
    save_config(config)
    await message.answer("✅ Текст благодарности обновлён.")

@dp.message(Command("set_broadcast_text"))
async def set_broadcast_text(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    new_text = message.text.replace("/set_broadcast_text", "").strip()
    if not new_text:
        await message.answer("Укажите текст после команды.")
        return
    config["broadcast_text"] = new_text
    save_config(config)
    await message.answer("✅ Текст рассылки обновлён.")

@dp.message(Command("set_broadcast_date"))
async def set_broadcast_date(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    date_str = message.text.replace("/set_broadcast_date", "").strip()
    try:
        dt = datetime.fromisoformat(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone(timedelta(hours=3)))
        config["broadcast_date"] = dt.isoformat()
        save_config(config)
        await message.answer(f"✅ Дата рассылки установлена: {dt.strftime('%d.%m.%Y %H:%M')} МСК")
        # Сбросим флаг отправки, чтобы рассылка могла сработать заново
        broadcast_sent_file = os.path.join(DATA_DIR, "broadcast_sent.txt")
        with open(broadcast_sent_file, 'w', encoding='utf-8') as f:
            f.write("False")
        await message.answer("Флаг рассылки сброшен. Если дата в будущем, бот будет ждать.")
    except Exception as e:
        await message.answer(f"Ошибка формата даты. Используйте ISO формат, например: 2026-06-15T12:00:00+03:00")

@dp.message(Command("set_winners"))
async def set_winners(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    try:
        count = int(message.text.replace("/set_winners", "").strip())
        if count < 1:
            raise ValueError
        config["winners_count"] = count
        save_config(config)
        await message.answer(f"✅ Количество победителей в розыгрыше установлено: {count}")
    except:
        await message.answer("Укажите целое положительное число, например: /set_winners 3")

@dp.message(F.text == "❌ Скрыть меню")
async def admin_hide(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    await state.clear()
    await message.answer("Меню скрыто", reply_markup=ReplyKeyboardRemove())

# ========== КОМАНДЫ ДЛЯ РУЧНОГО ВВОДА ==========
@dp.message(Command("participants"))
async def participants_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    await admin_participants(message)

@dp.message(Command("draw"))
async def draw_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    await admin_draw(message)

@dp.message(Command("check"))
async def check_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("использование: /check <id или @username>")
        return
    query = args[1].strip()
    found = find_participant(query)
    if not found:
        await message.answer("участник с таким ID или username не найден")
        return
    uid, full_name, username, filename = found
    path = os.path.join(SCREENSHOT_DIR, filename)
    caption = f"скриншот участника {full_name} (@{username}) (ID {uid}):"
    if os.path.exists(path):
        await message.answer_photo(FSInputFile(path), caption=caption)
    else:
        await message.answer(f"{caption}\n⚠️ файл скриншота не найден")

@dp.message(Command("broadcast"))
async def manual_broadcast(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    broadcast_sent_file = os.path.join(DATA_DIR, "broadcast_sent.txt")
    if os.path.exists(broadcast_sent_file):
        with open(broadcast_sent_file, 'r', encoding='utf-8') as f:
            sent = f.read().strip()
        if sent == "True":
            await message.answer("Рассылка уже была отправлена ранее.")
            return
    await message.answer("Запускаю ручную рассылку...")
    await send_broadcast()
    with open(PARTICIPANTS_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    await message.answer(f"✅ Рассылка завершена. Отправлено {len(lines)} участникам.")

@dp.message(Command("time_to_broadcast"))
async def time_to_broadcast_cmd(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("нет прав ))")
        return
    await admin_time_to_broadcast(message)

# ========== ЗАПУСК ==========
async def main():
    asyncio.create_task(schedule_broadcast())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
