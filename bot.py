# bot.py
from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.filters import Command
import database
import os
import random

# Список интересных фактов
FACTS = [
    "Знаешь ли ты, что первый программист — женщина? Её звали Ада Лавлейс.",
    "Смартфон сегодня мощнее, чем компьютеры, отправлявшие людей на Луну.",
    "Слово 'баг' (ошибка) появилось, когда в компьютер залетел настоящий мотылёк.",
    "Google зарабатывает больше на рекламе, чем все СМИ мира вместе взятые.",
    "В 2025 году в мире будет больше устройств, чем людей."
]

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

    # Кнопки под полем ввода
    kb = [
        [types.KeyboardButton(text="📚 Помощь"), types.KeyboardButton(text="👤 Профиль")],
        [types.KeyboardButton(text="🏆 Достижения"), types.KeyboardButton(text="🧠 Факт")],
        [types.KeyboardButton(text="⚙️ Настройки"), types.KeyboardButton(text="📊 WebApp")]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выбери команду..."
    )

    await message.answer(
        f"Привет, {user.first_name}! 👋\n"
        "Я — твой умный бот с веб-интерфейсом.\n"
        "Выбери, что хочешь сделать:",
        reply_markup=keyboard
    )

@dp.message(Command("admin"))
async def admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return
    all_actions = database.get_all_actions()
    text = "\n".join([f"[{a['time']}] {a['user']}: {a['action']}" for a in all_actions[:30]])
    await message.answer(f"📋 Последние 30 действий:\n\n{text}")

@dp.message(F.text == "📚 Помощь")
async def show_help(message: types.Message):
    text = (
        "📚 **Справка по боту**\n\n"
        "Команды:\n"
        "• /start — начать\n"
        "• /profile — твой профиль\n"
        "• /settings — настройки\n"
        "• /help — помощь\n\n"
        "Ты также можешь использовать кнопки ниже."
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "👤 Профиль")
async def show_profile(message: types.Message):
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

@dp.message(F.text == "⚙️ Настройки")
async def show_settings(message: types.Message):
    kb = [
        [types.InlineKeyboardButton(text="🔔 Уведомления", callback_data="settings_notify")],
        [types.InlineKeyboardButton(text="🎨 Тема", callback_data="settings_theme")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer("⚙️ Настройки", reply_markup=keyboard)

@dp.message(F.text == "📊 WebApp")
async def open_webapp(message: types.Message):
    kb = [[types.InlineKeyboardButton(text="📱 Открыть WebApp", web_app=types.WebAppInfo(url=WEBAPP_URL))]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer("Открой интерфейс:", reply_markup=keyboard)

@dp.message(Command("fact"))
async def cmd_fact(message: types.Message):
    user = message.from_user
    database.log_action(user.id, "viewed_fact")
    fact = random.choice(FACTS)
    await message.answer(f"🧠 <i>{fact}</i>", parse_mode="HTML")

@dp.message(Command("achievements"))
async def cmd_achievements(message: types.Message):
    user = message.from_user
    database.log_action(user.id, "viewed_achievements")

    # Получаем действия пользователя
    actions = database.get_user_actions(user.id)
    action_count = len(actions)

    # Определяем достижения
    achievements = []
    if action_count >= 5:
        achievements.append("🔥 Активный пользователь — сделал 5+ действий")
    if action_count >= 10:
        achievements.append("🏆 Мастер бота — 10+ действий")
    if any(a["action"] == "viewed_profile" for a in actions):
        achievements.append("👀 Любопытный — смотрел профиль")
    if any(a["action"] == "started_bot" for a in actions):
        achievements.append("👋 Новичок — только начал путь")

    # Формируем текст
    text = "🏆 <b>Твои достижения:</b>\n\n"
    if achievements:
        text += "\n".join(f"• {ach}" for ach in achievements)
    else:
        text += "Пока пусто... Но ты можешь это изменить!"

    await message.answer(text, parse_mode="HTML")
async def main():
    await dp.start_polling(bot)

@dp.message(F.text == "🏆 Достижения")
async def show_achievements(message: types.Message):
    await cmd_achievements(message)

@dp.message(F.text == "🧠 Факт")
async def show_fact(message: types.Message):
    await cmd_fact(message)
    
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())









