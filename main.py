import asyncio
import random
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandObject
from aiohttp import web
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from openai import AsyncOpenAI

# --- НАСТРОЙКИ (БЕРЕМ ИЗ ПЕРЕМЕННЫХ ОКРУЖЕНИЯ) ---
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
TARGET_CHAT_ID = -1003783490092

client = AsyncOpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
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

async def get_ai_response(prompt_text):
    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile", # Очень мощная модель
        messages=[
            {"role": "system", "content": "Ты эксперт по QA. Отвечай кратко."},
            {"role": "user", "content": prompt_text},
        ]
    )
    return response.choices[0].message.content

@dp.message(lambda message: message.reply_to_message and "❓" in message.reply_to_message.text)
async def check_answer_handler(message: types.Message):
    # Берем текст вопроса из оригинального сообщения бота
    question_text = message.reply_to_message.text
    # Берем то, что написал пользователь
    user_answer = message.text
    
# Формируем детальную инструкцию для работы над ошибками
    prompt = f"""
    Ты — ментор по тестированию ПО. Твоя задача — разобрать ответ ученика.
    Вопрос: {question_text}
    Ответ ученика: {user_answer}

    Действуй по шагам:
    1. Оцени ответ от 1/10 до 10/10.
    2. Найди в ответе ученика конкретные фразы, где мысль пошла не туда или где не хватает точности.
    3. Выдели эти места: напиши "Ошибка в мысли: [цитата]" и объясни, ПОЧЕМУ это не совсем верно или чего не хватает.
    4. Напиши исправленную версию конкретно этого момента.
    5. В конце дай краткий совет, как запомнить это правило лучше.

    Отвечай дружелюбно, как будто по братски, не стесняйся материться, можешь даже сильно материться чтоб легче было понять твою мысль ученику. Используй жирный шрифт для акцентов.
    """
    try:
        # Вызываем ту же функцию, что и в /quest
        ai_feedback = await get_ai_response(prompt)
        await message.reply(f"🤖 <b>Анализ твоего ответа:</b>\n\n{ai_feedback}", parse_mode="HTML")
    except Exception as e:
        print(f"Ошибка проверки: {e}")

@dp.message(Command("quest"))
async def ai_quest_handler(message: types.Message, command: CommandObject):
    if not command.args:
        return await message.reply("Напиши вопрос, например: /quest что такое баг?")
    
    msg = await message.answer("🤖 Как вы заебали со своими вопросами...")
    try:
        answer = await get_ai_response(command.args)
        await msg.edit_text(f"<b>Ответ ИИ:</b>\n\n{answer}", parse_mode="HTML")
    except Exception as e:
        await msg.edit_text(f"Ошибка DeepSeek: {e}")



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












