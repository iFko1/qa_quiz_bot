import asyncio
import random
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiohttp import web

# --- НАСТРОЙКИ ---
API_TOKEN = '8785404334:AAG97F8RrwtymAeMvnPpY0QVR1LzMEwknp8'
TARGET_CHAT_ID = -1003783490092  # ВСТАВЬ СВОЙ ID ТУТ (числом, без кавычек)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

TEAM = [
    {"name": "Динар", "tag": "@tat_dinero"},
    {"name": "Миша", "tag": "@mishka12f"},
    {"name": "Саша", "tag": "@beyo10"},
    {"name": "Женя", "tag": "@Attila607"}
]

# --- БАЗА ИЗ 50+ ВОПРОСОВ ---
QUESTIONS = [
    "Что такое 'Тестирование черного ящика'?",
    "В чем разница между Smoke и Sanity тестированием?",
    "Расскажи про жизненный цикл бага (Bug Life Cycle).",
    "Что такое граничные значения? Приведи пример для поля (1-10).",
    "Что такое эквивалентное разделение?",
    "Чем отличается Severity от Priority?",
    "Что такое регрессионное тестирование?",
    "Назови обязательные поля баг-репорта.",
    "В чем разница между Валидацией и Верификацией?",
    "Что делать, если баг не воспроизводится?",
    "Назови уровни тестирования по порядку.",
    "Зачем нужен чек-лист, если есть тест-кейсы?",
    "Что такое 'Принцип пестицида'?",
    "Что такое пирамида тестирования?",
    "В чем разница между GET и POST запросами?",
    "Что такое 7 принципов тестирования?",
    "Чем отличается ошибка от отказа (failure)?",
    "Что такое статическое тестирование?",
    "Приведи пример бага High Severity / Low Priority.",
    "Что такое исследовательское тестирование?",
    "Что такое нагрузочное тестирование?",
    "В чем разница между Альфа и Бета тестированием?",
    "Что такое матрица прослеживаемости (RTM)?",
    "Назови методы HTTP запросов.",
    "Что такое SQL и зачем он тестировщику?",
    "Что такое JSON?",
    "Как протестировать поле ввода имени?",
    "Что такое жизненный цикл ПО (SDLC)?",
    "Чем отличается мобильное тестирование от веба?",
    "Что такое эмулятор?",
    "Зачем нужна локализация?",
    "Что такое чек-лист?",
    "Что такое интеграционное тестирование?",
    "Как ты протестируешь карандаш?",
    "Что такое позитивное и негативное тестирование?",
    "Что такое GUI тестирование?",
    "Что такое функциональное тестирование?",
    "Что такое нефункциональное тестирование?",
    "Что такое системное тестирование?",
    "Что такое приемочное тестирование (UAT)?",
    "Что такое Тест-план?",
    "Что такое Тест-кейс?",
    "Что такое смоук-тест?",
    "Что такое кросс-браузерное тестирование?",
    "Что такое клиент-серверная архитектура?",
    "Что означает код ответа 404?",
    "Что означает код ответа 500?",
    "Что такое API?",
    "Что такое документация в тестировании?",
    "Какие техники тест-дизайна ты знаешь?",
    "Что такое тестирование удобства пользования?"
]
def get_random_member():
    return random.choice(TEAM)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("✅ Бот активен! Теперь Динар точно в списке.")

@dp.message(Command("quiz"))
async def manual_quiz(message: types.Message):
    # Явно выбираем участника прямо здесь
    member = get_random_member()
    question = random.choice(QUESTIONS)
    
    # Печатаем в лог для отладки (увидишь на Render)
    print(f"Выбран участник: {member['name']}")
    
    text = f"🎯 **Внеплановый опрос!**\n\n{member['tag']} ({member['name']}), твой выход:\n❓ {question}"
    await message.answer(text, parse_mode="Markdown")

async def send_hourly_quiz():
    if not TARGET_CHAT_ID:
        return
    
    member = get_random_member()
    question = random.choice(QUESTIONS)
    text = f"⏰ **Ежечасный опрос!**\n\n{member['tag']} ({member['name']}), настало твое время!\n❓ *{question}*"
    
    try:
        await bot.send_message(TARGET_CHAT_ID, text, parse_mode="Markdown")
    except Exception as e:
        print(f"Ошибка отправки: {e}")

# Заглушка для Render
async def handle(request):
    return web.Response(text="Bot is running!")

async def run_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    # Проверка раз в час
    scheduler.add_job(send_hourly_quiz, "interval", minutes=60)
    scheduler.start()
    
    await asyncio.gather(
        run_web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())

