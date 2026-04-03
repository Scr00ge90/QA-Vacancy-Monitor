import asyncio
import re
import random
import os
from datetime import datetime, date
from telethon import TelegramClient, events
from dotenv import load_dotenv
import atexit

# --- Загрузка переменных окружения ---
load_dotenv()

API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")

# --- PID файл ---
PID_FILE = "monitor_pid.txt"

with open(PID_FILE, "w") as f:
    f.write(str(os.getpid()))

def remove_pid():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

atexit.register(remove_pid)

# --- Клиент ---
client = TelegramClient("session", API_ID, API_HASH)

# --- КАНАЛЫ ---
CHANNELS = [
    "itvacancykz",
    "it_interns",
    "jobfortester",
    "workitkz",
    "qajoboffer",
    "jobforqa"
]

# --- ФИЛЬТРЫ ---
KEYWORDS = [
    "qa", "тестировщик", "manual qa",
    "junior", "стажер", "стажировка",
    "intern", "trainee", "без опыта"
]

EXCLUDE = [
    "senior", "lead", "middle 3+", "middle+", "5+ лет", "6+ лет"
]

# --- СООБЩЕНИЕ ---
MESSAGE_TEXT = """
Приветствую!

Ищу честный старт в профессии QA manual-тестировщика. Недавно закончил с отличием курс «Тестирование ПО с нуля до продвинутого — самый полный курс с практикой». Считаю, что для начинающего специалиста важнее стремление учиться и открытость, поэтому не завышаю опыт. Так же рассматриваю возможность стажировки. Параллельно делаю pet-проекты и прохожу обучением Selenium + Python.

Навыки и инструменты:
• Jira (баг-репорты, задачи)
• Chrome DevTools (анализ запросов и DOM)
• Postman (API)
• Charles Proxy (перехват трафика)
• Git (базовые команды, GitHub)

• Составляю чек-листы и тест-кейсы  
• Понимаю функциональное и нефункциональное тестирование  
• Тестирую требования (полнота, ясность, логика)  
• Работаю с User Story и спецификациями  

Базы данных:
• MySQL (SQL-запросы для проверки данных)
• MongoDB (Compass, работа с коллекциями)

Дополнительно:
• Тестирование мобильных приложений (Android Emulator)
• TestIT, Qase

Имею опыт в других сферах — это помогает понимать бизнес-процессы и находить риски.

Готов к стажировке, пробному периоду или полной занятости. Быстро обучаюсь и полностью включаюсь в работу.

Резюме прикрепил, при необходимости покажу примеры тестовой документации.

Хобби: настольный теннис (есть призовые места).

⚠️ P.S. Это сообщение отправлено с помощью моего pet-проекта — скрипта для мониторинга вакансий QA в Telegram.
Если вам неудобно — дайте знать, больше писать не буду.
"""

# --- НАСТРОЙКИ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_PATH = os.path.join(BASE_DIR, "Пак_Виталий_Владимирович.pdf")

DELAY_MIN = 60
DELAY_MAX = 120
MAX_MESSAGES_PER_DAY = 25
SAFE_MODE = os.getenv("SAFE_MODE", "true").lower() == "true"  # По умолчанию безопасный режим

LOG_DIR = os.path.join(BASE_DIR, "logs")
ARCHIVE_DIR = os.path.join(LOG_DIR, "archive")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# --- Состояние ---
sent_users = set()
sent_today = 0
last_run_date = date.today()

def get_log_file(for_date=None):
    d = for_date or date.today()
    return os.path.join(LOG_DIR, f"sent_log_{d.strftime('%Y-%m-%d')}.txt")

LOG_FILE = get_log_file()

# --- Загрузка уже отправленных ---
def load_sent_users():
    global sent_users
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.split("|")
                if parts:
                    sent_users.add(parts[0].strip())

load_sent_users()

# --- Извлечение username ---
def extract_usernames(text):
    return re.findall(r'@[\w\d_]+', text)

# --- Сброс счётчика при смене дня ---
def reset_daily_state():
    global sent_today, last_run_date, sent_users, LOG_FILE

    old_log = get_log_file(last_run_date)
    if os.path.exists(old_log):
        archive_path = os.path.join(ARCHIVE_DIR, os.path.basename(old_log))
        os.rename(old_log, archive_path)

    sent_today = 0
    last_run_date = date.today()
    LOG_FILE = get_log_file()
    sent_users.clear()
    load_sent_users()

# --- Обработка новых сообщений ---
@client.on(events.NewMessage(chats=CHANNELS))
async def handler(event):
    global sent_today

    if date.today() != last_run_date:
        reset_daily_state()

    if sent_today >= MAX_MESSAGES_PER_DAY:
        return

    text = event.message.message
    if not text:
        return

    text_lower = text.lower()

    if not any(k in text_lower for k in KEYWORDS):
        return
    if any(bad in text_lower for bad in EXCLUDE):
        return
    if not any(w in text_lower for w in ["junior", "стаж", "intern"]):
        return

    usernames = extract_usernames(text)
    if not usernames:
        return

    print(f"\n[НАЙДЕНА ВАКАНСИЯ]\n{text[:200]}...\n")

    for username in usernames:
        username = username.strip()

        if username.lower().endswith("bot"):
            continue
        if username in sent_users:
            continue

        try:
            if SAFE_MODE:
                print(f"[SAFE MODE] Найден контакт: {username}")
                continue

            await client.send_message(username, MESSAGE_TEXT)

            if FILE_PATH and os.path.exists(FILE_PATH):
                await client.send_file(username, FILE_PATH)

            sent_users.add(username)
            sent_today += 1

            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"{username} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {text[:80].strip()}...\n")

            print(f"[OK] Отправлено: {username} | Сегодня: {sent_today}/{MAX_MESSAGES_PER_DAY}")

            await asyncio.sleep(random.randint(DELAY_MIN, DELAY_MAX))

        except Exception as e:
            print(f"[ERROR] {username}: {e}")

# --- Главная функция ---
async def main():
    print(f"[CONFIG] SAFE_MODE = {SAFE_MODE}")
    print(f"[CONFIG] MAX_MESSAGES_PER_DAY = {MAX_MESSAGES_PER_DAY}")
    print(f"[CONFIG] Каналы: {', '.join(CHANNELS)}")
    print("-" * 40)

    while True:
        try:
            await client.start()
            print("[START] Скрипт запущен, мониторинг активен...")
            await client.run_until_disconnected()
        except Exception as e:
            print(f"[ERROR] {e}. Перезапуск через 60 секунд...")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
