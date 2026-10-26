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
# 👇 ТОКЕН ВСТАВЛЕН СЮДА 👇
BOT_TOKEN = os.getenv("BOT_TOKEN", "1780243260:JsuCWrdBDfMjPxmH2JRVNZ9hREvWYzDZ0fe")
API_BASE = os.getenv("API_BASE", "https://misugram.cloud-ip.cc")

# --- Flask для Render (чтобы сервис не засыпал) ---
app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health():
    return "Bot is running", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- Подключение к кастомному шлюзу ---
session = AiohttpSession(
    api=TelegramAPIServer.from_base(API_BASE)
)
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
        f"Работаю и в личке, и в чатах. Напиши что угодно."
    )

@dp.message(Command("nahui"))
async def cmd_nahui(message: Message):
    name = message.from_user.first_name or "друг"
    await message.reply(random.choice(PHRASES).format(name=name))

@dp.message(F.text, F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}))
async def group_text(message: Message):
    bot_username = (await bot.me()).username
    is_mention = f"@{bot_username}" in (message.text or "")
    is_reply_to_bot = (
        message.reply_to_message is not None
        and message.reply_to_message.from_user is not None
        and message.reply_to_message.from_user.id == (await bot.me()).id
    )
    if not (is_mention or is_reply_to_bot):
        return
    name = message.from_user.first_name or "друг"
    await message.reply(random.choice(PHRASES).format(name=name))

@dp.message(F.text, F.chat.type == ChatType.PRIVATE)
async def private_text(message: Message):
    name = message.from_user.first_name or "друг"
    await message.reply(random.choice(PHRASES).format(name=name))

async def main():
    logging.basicConfig(level=logging.INFO)
    me = await bot.get_me()
    logging.info(f"Запущен бот @{me.username} через {API_BASE}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Запускаем Flask в фоне, чтобы Render видел открытый порт
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())
