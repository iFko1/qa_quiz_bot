import asyncio
import random
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler # Добавили импорт

# --- НАСТРОЙКИ ---
API_TOKEN = '8785404334:AAG97F8RrwtymAeMvnPpY0QVR1LzMEwknp8' # ВАЖНО: смени токен после запуска!
TARGET_CHAT_ID = -1003783490092

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler() # Создали объект планировщика

TEAM = [
    {"name": "Динар", "tag": "@tat_dinero"},
    {"name": "Миша", "tag": "@mishka12f"},
    {"name": "Саша", "tag": "@beyo10"},
    {"name": "Женя", "tag": "@Attila607"}
]

QUESTIONS = [
    "Чем тестирование (testing) отличается от обеспечения качества (QA) и контроля качества (QC)?",
    "Назовите семь принципов тестирования. Раскройте один из них (например, «Парадокс пестицида» или «Исчерпывающее тестирование невозможно»)",
    "Расскажи про жизненный цикл бага (Bug Life Cycle).",
    "Что такое граничные значения? Приведи пример для поля (1-10).",
    "Что такое эквивалентное разделение?",
    "Чем отличается Severity от Priority?",
    "Что такое регрессионное тестирование?",
    "Назови обязательные поля баг-репорта.",
    "Какие виды требований вы знаете? Что делать, если требования отсутствуют или противоречивы?",
    "Что делать, если баг не воспроизводится?",
    "Когда следует начинать тестирование в проекте и почему?",
    "Зачем нужен чек-лист, если есть тест-кейсы?",
    "Что такое 'Принцип пестицида'?",
    "Что такое предугадывание ошибок (Error Guessing)? Приведите пример",
    "В чем разница между позитивным и негативным тестированием? Почему важно начинать с позитивного?",
    "Как понять, что тестирование можно завершать?",
    "Что такое попарное тестирование (Pairwise Testing) и для чего оно используется?",
    "Что такое Use Case? Чем он отличается от тест-кейса?",
    "Как устроена клиент-серверная архитектура?",
    "Что такое HTTP? Из чего состоит HTTP-запрос и HTTP-ответ?",
    "В чем разница между кодами 401 (Unauthorized) и 403 (Forbidden)?",
    "В чем разница между Альфа и Бета тестированием?",
    "Чем REST отличается от SOAP?",
    "Назови методы HTTP запросов.",
    "Что такое SQL и зачем он тестировщику?",
    "Что такое JSON?",
    "Напишите SQL-запрос с JOIN для выборки данных из двух связанных таблиц.",
    "Что такое жизненный цикл ПО (SDLC)?",
    "Что такое первичный ключ (Primary Key) и внешний ключ (Foreign Key)?",
    "Для чего тестировщику нужно уметь читать и писать SQL-запросы?",
    "Зачем нужна локализация?",
    "Что такое чек-лист?",
    "Что такое интеграционное тестирование?",
    "Как ты протестируешь карандаш?",
    "Что такое позитивное и негативное тестирование?",
    "Что такое снифферы трафика (Charles, Fiddler)? Для чего их используют в тестировании мобильных приложений и веба?",
    "Как с помощью DevTools проанализировать, почему страница долго грузится?",
    "Что такое логи? Где искать логи? Как тестировщик может использовать логи для поиска причин падения?",
    "Что такое CI/CD? Какие инструменты CI вы знаете?",
    "Что такое Git? Какие основные команды Git вы знаете?",
    "Что такое Тест-план?",
    "Что такое Тест-кейс?",
    "Что такое смоук-тест?",
    "Что такое Docker? Для чего он нужен в тестировании?",
    "Что такое клиент-серверная архитектура?",
    "Что означает код ответа 404?",
    "Что означает код ответа 500?",
    "Что такое API?",
    "Что такое документация в тестировании?",
    "Расскажите о самом сложном баге, который вы находили. Как вы его искали и как доказывали разработчикам?",
    "Сосал?",
    "Что такое Agile, Scrum? В каких церемониях вы участвуете?",
    "Как вы доносите информацию о критическом баге до команды за день до релиза? Ваши действия.",
    "Как выстраивать коммуникацию с разработчиком, который не считает нужным тестировать свой код перед передачей вам?"
]

@dp.message(Command("quiz"))
async def quiz_handler(message: types.Message):
    member = random.choice(TEAM)
    question = random.choice(QUESTIONS)
    text = f"🎯 <b>Опрос для {member['name']}!</b>\n\n{member['tag']}\n❓ <i>{question}</i>"
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("dinar"))
async def dinar_handler(message: types.Message):
    member = {"name": "Динар", "tag": "@tat_dinero"}
    question = random.choice(QUESTIONS)
    text = f"🎯 <b>Специальный вопрос для Динара!</b>\n\n{member['tag']}\n❓ <i>{question}</i>"
    await message.answer(text, parse_mode="HTML")

async def handle(request):
    return web.Response(text="Bot is running!")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080)))
    await site.start()

async def send_hourly_quiz():
    member = random.choice(TEAM)
    question = random.choice(QUESTIONS)
    text = f"⏰ <b>Ежечасный опрос!</b>\n\n{member['tag']} ({member['name']}), твой вопрос:\n❓ <i>{question}</i>"
    try:
        await bot.send_message(TARGET_CHAT_ID, text, parse_mode="HTML")
    except Exception as e:
        print(f"Ошибка автоматической отправки: {e}")

async def main():
    scheduler.add_job(send_hourly_quiz, "interval", minutes=60)
    scheduler.start()
    await asyncio.gather(start_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())

