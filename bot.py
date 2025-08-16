# bot.py
from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.filters import Command
import database
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = "https://kugjj.github.io"  # ⚠️ ПОМЕНЯЙ!
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

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    text = (
        "📚 **Справка по боту**\n\n"
        "Команды:\n"
        "• /start — начать\n"
        "• /profile — твой профиль\n"
        "• /settings — настройки (в разработке)\n"
        "• /help — помощь\n\n"
        "WebApp показывает твои действия и статистику."
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    user = message.from_user
    database.log_action(user.id, "viewed_profile")
    text = (
        "👤 **Твой профиль**\n\n"
        f"• Имя: {user.first_name}\n"
        f"• Юзернейм: @{user.username or 'не указан'}\n"
        f"• ID: `{user.id}`\n"
        f"• Язык: {user.language_code}"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("settings"))
async def cmd_settings(message: types.Message):
    kb = [
        [types.InlineKeyboardButton(text="🔔 Уведомления", callback_data="settings_notify")],
        [types.InlineKeyboardButton(text="🎨 Тема", callback_data="settings_theme")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer("⚙️ Настройки", reply_markup=keyboard)

@dp.callback_query(F.data == "settings_notify")
async def settings_notify(callback: types.CallbackQuery):
    await callback.answer("Уведомления включены!")

@dp.callback_query(F.data == "settings_theme")
async def settings_theme(callback: types.CallbackQuery):
    await callback.answer("Тема: светлая")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())






