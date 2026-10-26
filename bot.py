import asyncio
import logging
import os
import random
import threading
from flask import Flask

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message

# --- Конфиг ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "1780243260:3bxfqgTpFf7Ip1z7bZEwkHT5zn5eQeCo1qd")
API_BASE = os.getenv("API_BASE", "https://misugram.cloud-ip.cc")

# --- Flask для Render ---
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "Bot is running", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Подключение к шлюзу ---
session = AiohttpSession(api=TelegramAPIServer.from_base(API_BASE))
bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher()

PHRASES = [
    "Иди нахуй, {name}. Не пиши сюда больше.",
    "{name}, ты знаешь куда идти? Нахуй. Вперёд.",
    "Слушай, {name}, уёбывай нахуй, у меня нет времени.",
    "{name}, искренне желаю тебе пройти нахуй. Прямо сейчас.",
    "Нахуй иди, {name}. С уважением, бот.",
    "{name}, твой маршрут построен: прямо, потом нахуй.",
    "Извини, {name}, но единственный адрес, который я могу тебе дать — нахуй.",
    "{name}, не зли меня. Иди нахуй, пожалуйста.",
]

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}. Я бот, который посылает нахуй. "
        f"Работаю и в личке, и в чатах."
    )

# --- РАБОТА В ЧАТАХ (ОТВЕЧАЕТ НА ВСЁ) ---
@dp.message(F.text, F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def group_text(message: Message):
    # Убираем все проверки на упоминания. Отвечаем на любое текстовое сообщение.
    name = message.from_user.first_name or "друг"
    await message.reply(random.choice(PHRASES).format(name=name))

# --- РАБОТА В ЛИЧКЕ ---
@dp.message(F.text, F.chat.type == ChatType.PRIVATE)
async def private_text(message: Message):
    name = message.from_user.first_name or "друг"
    await message.reply(random.choice(PHRASES).format(name=name))

async def main():
    logging.basicConfig(level=logging.INFO)
    me = await bot.get_me()
    logging.info(f"Запущен бот @{me.username} через {API_BASE}")
    
    # Очищаем вебхуки, чтобы избежать конфликтов
    await bot.delete_webhook(drop_pending_updates=True)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())
