# bot.py
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import database
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = "https://your-github-username.github.io/telegram-webapp"  # ⚠️ ПОМЕНЯЙ!
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: types.Message):
    user = message.from_user
    database.add_user({
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name
    })
    database.log_action(user.id, "started_bot")

    kb = [[types.InlineKeyboardButton(text="📱 Открыть интерфейс", web_app=types.WebAppInfo(url=WEBAPP_URL))]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer(f"Привет, {user.first_name}! 👋\nНажми кнопку ниже, чтобы открыть интерфейс.", reply_markup=keyboard)

@dp.message(Command("admin"))
async def admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return
    all_actions = database.get_all_actions()
    text = "\n".join([f"[{a['time']}] {a['user']}: {a['action']}" for a in all_actions[:30]])
    await message.answer(f"📋 Последние 30 действий:\n\n{text}")

async def main():
    await dp.start_polling(bot)