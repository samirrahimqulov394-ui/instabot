import asyncio
import logging
import os
import random
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

if not TOKEN:
    raise ValueError("Xatolik: BOT_TOKEN muhit o'zgaruvchisi topilmadi!")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ----------------------------------------------------
# KATTA SAVOLLAR BAZASI (Xohlagancha ko'paytirishingiz mumkin)
# ----------------------------------------------------
QUESTIONS_BANK = [
    {
        "question": "1. Choose the correct pronoun:\n'___ am a student.'",
        "options": ["He", "I", "They", "We"],
        "correct": 1
    },
    {
        "question": "2. What is the plural form of 'child'?",
        "options": ["Childs", "Children", "Childes", "Kids"],
        "correct": 1
    },
    {
        "question": "3. Choose the correct verb form:\n'She ___ to school every day.'",
        "options": ["go", "goes", "going", "gone"],
        "correct": 1
    },
    {
        "question": "4. Opposite of the word 'Big' is:",
        "options": ["Huge", "Large", "Small", "Tall"],
        "correct": 2
    },
    {
        "question": "5. Complete the sentence:\n'They ___ watching a movie right now.'",
        "options": ["is", "am", "are", "be"],
        "correct": 2
    },
    {
        "question": "6. Which past tense form is CORRECT?",
        "options": ["Buyed", "Bought", "Buyedness", "Bringed"],
        "correct": 1
    },
    {
        "question": "7. Choose the correct preposition:\n'He was born ___ May.'",
        "options": ["on", "at", "in", "by"],
        "correct": 2
    },
    {
        "question": "8. What is the comparative form of 'Good'?",
        "options": ["Gooder", "Better", "Best", "More good"],
        "correct": 1
    }
]

# ----------------------------------------------------
# FSM HOLATLARI (Test va Sharh yozish uchun)
# ----------------------------------------------------
class TestState(StatesGroup):
    in_test = State()

class FeedbackState(StatesGroup):
    waiting_for_feedback = State()

# ----------------------------------------------------
# BOSH MENYU
# ----------------------------------------------------
def main_menu_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Testni boshlash (8 ta savol)", callback_data="start_test")],
        [
            InlineKeyboardButton(text="✍️ Sharh / Fikr qoldirish", callback_data="leave_feedback"),
            InlineKeyboardButton(text="ℹ️ Bot haqida", callback_data="about")
        ]
    ])

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_name = message.from_user.first_name

    await message.answer(
        f"Assalomu alaykum, {user_name}!\n\n"
        f"\"English Question\" botiga xush kelibsiz! Test ishlashingiz yoki bot haqida o'z sharhingizni yozib qoldirishingiz mumkin.",
        reply_markup=main_menu_keyboard()
    )

@dp.callback_query(F.data == "back_home")
async def process_home(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_name = callback.from_user.first_name
    await callback.message.edit_text(
        f"Assalomu alaykum, {user_name}!\n\n"
        f"Bosh menyuga qaytdingiz. Kerakli bo'limni tanlang:",
        reply_markup=main_menu_keyboard()
    )

# ----------------------------------------------------
# SHARH / FIKR QOLDIRISH BO'LIMI
# ----------------------------------------------------
@dp.callback_query(F.data == "leave_feedback")
async def process_feedback_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(FeedbackState.waiting_for_feedback)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="back_home")]
    ])
    
    await callback.message.edit_text(
        "✍️ **Botingiz va savollar haqidagi fikringizni yozib yuboring:**\n\n"
        "Matn yozib yuborsangiz, u adminga yetkaziladi va botni yaxshilashga yordam beradi.",
        reply_markup=keyboard
    )

@dp.message(FeedbackState.waiting_for_feedback)
async def process_feedback_received(message: Message, state: FSMContext):
    user_info = message.from_user.full_name
    username = f"@{message.from_user.username}" if message.from_user.username else "Usernamelar yo'q"
    feedback_text = message.text

    logging.info(f"Yangi sharh [{user_info} - {username}]: {feedback_text}")

    await state.clear()
    await message.answer(
        "✅ **Katta rahmat! Sharhingiz qabul qilindi.**\n\n"
        "Fikringiz botimizni yanada mukammal qilish uchun xizmat qiladi.",
        reply_markup=main_menu_keyboard()
    )

# ----------------------------------------------------
# TEST JARAYONI (Random savollar bilan)
# ----------------------------------------------------
@dp.callback_query(F.data == "about")
async def process_about(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "ℹ️ **Bot haqida:**\n\n"
        "Ushbu bot ingliz tili savollari bazasidan random shaklda savollar beradi va darajangizni aniqlaydi.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_home")]
        ])
    )

@dp.callback_query(F.data == "start_test")
async def start_test(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Savollarni har safar tasodifiy tartibda aralashtiramiz
    user_questions = QUESTIONS_BANK.copy()
    random.shuffle(user_questions)

    await state.set_state(TestState.in_test)
    await state.update_data(questions=user_questions, question_index=0, score=0)
    await send_question(callback.message, state, edit=True)

async def send_question(message: Message, state: FSMContext, edit: bool = False):
    data = await state.get_data()
    questions = data.get("questions", [])
    q_index = data.get("question_index", 0)

    if q_index >= len(questions):
        score = data.get("score", 0)
        total = len(questions)
        await state.clear()
        
        # Natijaga qarab baholash
        percent = (score / total) * 100
        status = "🌟 Mukammal!" if percent >= 80 else "👍 Yomon emas!" if percent >= 50 else "📚 Yanada ko'proq o'qishingiz kerak!"

        text = (
            f"🎉 **Test yakunlandi!**\n\n"
            f"📊 Sizning natijangiz: **{score} / {total}** ({int(percent)}%)\n"
            f"Baho: {status}"
        )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Qaytadan boshlash", callback_data="start_test")],
            [InlineKeyboardButton(text="✍️ Sharh qoldirish", callback_data="leave_feedback")],
            [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_home")]
        ])
        
        if edit:
            await message.edit_text(text, reply_markup=keyboard)
        else:
            await message.answer(text, reply_markup=keyboard)
        return

    q = questions[q_index]

    keyboard_buttons = []
    for i, option in enumerate(q["options"]):
        keyboard_buttons.append([InlineKeyboardButton(text=option, callback_data=f"ans_{i}")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    
    if edit:
        await message.edit_text(q["question"], reply_markup=keyboard)
    else:
        await message.answer(q["question"], reply_markup=keyboard)

@dp.callback_query(F.data.startswith("ans_"), TestState.in_test)
async def check_answer(callback: CallbackQuery, state: FSMContext):
    selected_ans = int(callback.data.split("_")[1])

    data = await state.get_data()
    questions = data.get("questions")
    q_index = data.get("question_index")
    score = data.get("score")

    q = questions[q_index]

    if selected_ans == q["correct"]:
        score += 1
        await callback.answer("✅ To'g'ri!", show_alert=False)
    else:
        correct_text = q["options"][q["correct"]]
        await callback.answer(f"❌ Xato! To'g'ri javob: {correct_text}", show_alert=True)

    await state.update_data(question_index=q_index + 1, score=score)
    await send_question(callback.message, state, edit=True)


# --- RENDER WEB SERVER ---
async def handle(request):
    return web.Response(text="English Question Bot Active!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
