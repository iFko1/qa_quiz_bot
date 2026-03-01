import asyncio
import random
import os
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- НАСТРОЙКИ (БЕРЕМ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ) ---
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
TARGET_CHAT_ID = -1003783490092

# Настройка ИИ (Gemini 2.0 Flash)
if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=API_TOKEN) if API_TOKEN else None
dp = Dispatcher()
scheduler = AsyncIOScheduler()

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

def get_ai_response(prompt_text):
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt_text)

@dp.message(Command("quest"))
async def ai_quest_handler(message: types.Message, command: CommandObject):
    if not command.args:
        return await message.reply("Напиши вопрос после команды.")
    
    msg = await message.answer("🤖 Секунду...")
    try:
        # Прямой вызов с получением ключа в момент запроса
        answer = get_ai_response(command.args)
        await msg.edit_text(f"<b>Ответ ИИ:</b>\n\n{answer}", parse_mode="HTML")
    except Exception as e:
        print(f"Full Error: {e}") # Это уйдет в логи Render
        await msg.edit_text(f"Ошибка: {e}")



# Проверка ответа (Reply)
@dp.message(lambda message: message.reply_to_message and "❓" in message.reply_to_message.text)
async def check_answer(message: types.Message):
    try:
        response = ai_model.generate_content(f"Вопрос: {message.reply_to_message.text}. Ответ: {message.text}. Оцени кратко.")
        await message.reply(f"🤖 <b>Вердикт:</b>\n{response.text}", parse_mode="HTML")
    except: pass

# Команды /quiz и /dinar
@dp.message(Command("quiz"))
async def quiz_handler(message: types.Message):
    m = random.choice(TEAM)
    q = random.choice(QUESTIONS)
    await message.answer(f"🎯 <b>Опрос для {m['name']}!</b>\n\n{m['tag']}\n❓ <i>{q}</i>", parse_mode="HTML")

@dp.message(Command("dinar"))
async def dinar_handler(message: types.Message):
    q = random.choice(QUESTIONS)
    await message.answer(f"🎯 <b>Специально для Динара!</b>\n\n@tat_dinero\n❓ <i>{q}</i>", parse_mode="HTML")

async def send_hourly_quiz():
    m = random.choice(TEAM)
    q = random.choice(QUESTIONS)
    try: await bot.send_message(TARGET_CHAT_ID, f"⏰ <b>Ежечасный опрос!</b>\n\n{m['tag']}\n❓ <i>{q}</i>", parse_mode="HTML")
    except: pass

async def handle(request): return web.Response(text="Bot Live")

async def main():
    scheduler.add_job(send_hourly_quiz, "interval", minutes=60)
    scheduler.start()
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080))).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())






