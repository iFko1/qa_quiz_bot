import asyncio
import random
import os
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- НАСТРОЙКИ (БЕРЕМ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ) ---
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN') # Бот сам возьмет это из настроек Render
GEMINI_KEY = os.getenv('GEMINI_API_KEY')     # И это тоже
TARGET_CHAT_ID = -1003783490092

# Проверка, что ключи загружены (для отладки в логах)
if not API_TOKEN or not GEMINI_KEY:
    print("ОШИБКА: Ключи API не найдены в переменных окружения!")

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

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

@dp.message(Command("quest"))
async def ai_quest_handler(message: types.Message, command: CommandObject):
    if not command.args:
        return await message.reply("Напиши вопрос после команды, например: <code>/quest что такое API?</code>", parse_mode="HTML")
    
    msg = await message.answer("🤖 Ищу ответ в своих нейронных связях...")
    
    prompt = f"Ты эксперт по тестированию ПО. Кратко и понятно ответь на вопрос: {command.args}"
    
    try:
        response = ai_model.generate_content(prompt)
        await msg.edit_text(f"<b>Ответ ИИ:</b>\n\n{response.text}", parse_mode="HTML")
    except Exception as e:
        await msg.edit_text("Не удалось связаться с ИИ. Попробуй позже.")
        
@dp.message(Command("quiz"))
async def quiz_handler(message: types.Message):
    member = random.choice(TEAM)
    question = random.choice(QUESTIONS)
    text = f"🎯 <b>Опрос для {member['name']}!</b>\n\n{member['tag']}\n❓ <i>{question}</i>"
    await message.answer(text, parse_mode="HTML")

@dp.message(lambda message: message.reply_to_message and ("❓" in message.reply_to_message.text or "🎯" in message.reply_to_message.text))
async def check_answer(message: types.Message):
    question_text = message.reply_to_message.text
    user_answer = message.text
    
    prompt = f"Вопрос по QA: {question_text}. Ученик ответил: {user_answer}. Оцени ответ по 10-балльной шкале, кратко поправь ошибки и дай правильный лаконичный ответ."
    
    try:
        response = ai_model.generate_content(prompt)
        await message.reply(f"🤖 <b>Анализ ответа:</b>\n\n{response.text}", parse_mode="HTML")
    except Exception:
        pass # Игнорируем ошибки ИИ здесь

# 3. СТАРЫЕ КОМАНДЫ (Quiz, Dinar)
@dp.message(Command("quiz"))
async def quiz_handler(message: types.Message):
    member = random.choice(TEAM)
    question = random.choice(QUESTIONS)
    text = f"🎯 <b>Опрос для {member['name']}!</b>\n\n{member['tag']}\n❓ <i>{question}</i>"
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("dinar"))
async def dinar_handler(message: types.Message):
    question = random.choice(QUESTIONS)
    text = f"🎯 <b>Специально для Динара!</b>\n\n@tat_dinero\n❓ <i>{question}</i>"
    await message.answer(text, parse_mode="HTML")

# --- СЛУЖЕБНЫЕ ФУНКЦИИ ---
async def send_hourly_quiz():
    member = random.choice(TEAM)
    question = random.choice(QUESTIONS)
    text = f"⏰ <b>Ежечасный опрос!</b>\n\n{member['tag']} ({member['name']})\n❓ <i>{question}</i>"
    try:
        await bot.send_message(TARGET_CHAT_ID, text, parse_mode="HTML")
    except: pass

async def handle(request): return web.Response(text="Live")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv("PORT", 8080)))
    await site.start()

async def main():
    scheduler.add_job(send_hourly_quiz, "interval", minutes=60)
    scheduler.start()
    await asyncio.gather(start_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())



