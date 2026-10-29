import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Bot tokeni
TOKEN = "9019628067:AAEoJWLLx0D7lKPmruIZoItOAvEHeitl9zQ"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Test savollari bazasi (A1 daraja)
QUESTIONS = [
    {
        "question": "1. Choose the correct pronoun: '___ am a student.'",
        "options": ["He", "I", "They", "We"],
        "correct": 1
    },
    {
        "question": "2. What is the plural form of 'child'?",
        "options": ["Childs", "Children", "Childes", "Kid"],
        "correct": 1
    },
    {
        "question": "3. Choose the correct verb: 'She ___ to school every day.'",
        "options": ["go", "goes", "going", "gone"],
        "correct": 1
    }
]

# FSM holatlari (Test jarayoni uchun)
class TestState(StatesGroup):
    in_test = State()
    question_index = State()
    score = State()

# /start komandasi
@dp.message(Command("start"))
async def cmd_start(message: Message):
    user_name = message.from_user.first_name
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Testni boshlash (A1)", callback_data="start_test")],
        [
            InlineKeyboardButton(text="📊 Natijalarim", callback_data="my_stats"),
            InlineKeyboardButton(text="ℹ️ Bot haqida", callback_data="about")
        ]
    ])
    
    await message.answer(
        f"Assalomu alaykum, {user_name}!\n\n"
        f"\"English Question\" botiga xush kelibsiz. Ingliz tili bilimingizni sinash uchun pastdagi tugmani bosing.",
        reply_markup=keyboard
    )

# Bot haqida
@dp.callback_query(F.data == "about")
async def process_about(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Bu bot ingliz tili bo'yicha testlar topshirish va darajani aniqlash uchun yaratilgan.")

# Testni boshlash
@dp.callback_query(F.data == "start_test")
async def start_test(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(TestState.in_test)
    await state.update_data(question_index=0, score=0)
    await send_question(callback.message, state)

# Savolni yuborish funksiyasi
async def send_question(message: Message, state: FSMContext):
    data = await state.get_data()
    q_index = data.get("question_index")
    
    if q_index >= len(QUESTIONS):
        score = data.get("score")
        total = len(QUESTIONS)
        await state.clear()
        await message.answer(
            f"🎉 **Test yakunlandi!**\n\n"
            f"Sizning natijangiz: {score} ta to'g'ri javob {total} tadan.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Qaytadan boshlash", callback_data="start_test")]
            ])
        )
        return

    q = QUESTIONS[q_index]
    
    keyboard_buttons = []
    for i, option in enumerate(q["options"]):
        keyboard_buttons.append([InlineKeyboardButton(text=option, callback_data=f"ans_{i}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await message.answer(q["question"], reply_markup=keyboard)

# Javobni tekshirish
@dp.callback_query(F.data.startswith("ans_"), TestState.in_test)
async def check_answer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    selected_ans = int(callback.data.split("_")[1])
    
    data = await state.get_data()
    q_index = data.get("question_index")
    score = data.get("score")
    
    q = QUESTIONS[q_index]
    
    if selected_ans == q["correct"]:
        score += 1
        await callback.message.answer("✅ To'g'ri!")
    else:
        correct_text = q["options"][q["correct"]]
        await callback.message.answer(f"❌ Xato! To'g'ri javob: {correct_text}")
    
    await state.update_data(question_index=q_index + 1, score=score)
    await send_question(callback.message, state)


# --- RENDER UCHUN WEB SERVER QISMI ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render beradigan portni oladi (agar bo'lmasa 8080 ishlatadi)
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on port {port}")


# Asosiy ishga tushirish funksiyasi
async def main():
    # Veb-serverni va bot pollingni bir vaqtda yurgazish
    await web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
