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
import google.generativeai as genai

# --- TOKENLAR VA SOZLAMALAR ---
BOT_TOKEN = "9019628067:AAEoJWLLx0D7lKPmruIZoItOAvEHeitl9zQ"
GEMINI_API_KEY = "AQ.Ab8RN6JQAGCed-mdVRbZqF7LeTNvZxG"  # Siz nusxalagan Gemini API kaliti

# Gemini AI ni sozlash
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- FSM STATE (Holatlar) ---
class BotStates(StatesGroup):
    ai_chat = State()        # AI bilan erkin suhbatlashish
    waiting_feedback = State() # Sharh yozish

# --- BOSH MENYU ---
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤖 AI Repetitor bilan suhbat", callback_data="start_ai")],
        [InlineKeyboardButton(text="🧠 Gemini dan Test olish", callback_data="ai_quiz")],
        [InlineKeyboardButton(text="💡 Kun iborasi (Daily Idiom)", callback_data="daily_idiom")],
        [InlineKeyboardButton(text="✍️ Sharh / Fikr qoldirish", callback_data="feedback")]
    ])

@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_name = message.from_user.first_name
    await message.answer(
        f"Assalomu alaykum, {user_name}!\n\n"
        f"🌟 **Super English AI Bot**ga xush kelibsiz! Bu bot Google Gemini sun'iy intellekti bilan jihozlangan.\n\n"
        f"Quyidagi bo'limlardan birini tanlang:",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "back_home")
async def back_to_home(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "🏠 **Bosh menyu:**\nKerakli bo'limni tanlang:",
        reply_markup=main_menu()
    )

# --- 1. AI CHAT (Ingliz tilida suhbatlashish va grammatika) ---
@dp.callback_query(F.data == "start_ai")
async def start_ai_chat(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(BotStates.ai_chat)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Chatni to'xtatish", callback_data="back_home")]
    ])
    
    await callback.message.edit_text(
        "🤖 **AI Repetitor bilan chat boshlandi!**\n\n"
        "Menga ingliz tilida xohlagan narsangizni yozing. Men siz bilan suhbatlashaman va grammatik xatolaringiz bo'lsa, ularni o'zbek tilida tushuntirib beraman.",
        reply_markup=keyboard
    )

@dp.message(BotStates.ai_chat)
async def handle_ai_chat(message: Message):
    user_text = message.text
    
    prompt = (
        f"You are a friendly English teacher. The user said: '{user_text}'. "
        "Reply naturally in English to continue the conversation. "
        "If there are any grammar or vocabulary mistakes in the user's sentence, politely correct them in Uzbek at the end of your message."
    )
    
    try:
        response = gemini_model.generate_content(prompt)
        await message.answer(response.text)
    except Exception as e:
        logging.error(f"Gemini error: {e}")
        await message.answer("⚠️ AI javob berishda xatolik yuz berdi. Birozdan keyin qayta urinib ko'ring.")

# --- 2. GEMINI DAN TEST OLISH ---
@dp.callback_query(F.data == "ai_quiz")
async def generate_ai_quiz(callback: CallbackQuery):
    await callback.answer("Gemini savol tayyorlamoqda...")
    
    prompt = (
        "Generate 1 multiple-choice English grammar question with 4 options. "
        "Provide the correct answer explanation in Uzbek language. Format it nicely."
    )
    
    try:
        response = gemini_model.generate_content(prompt)
        await callback.message.edit_text(
            f"🧠 **AI tomonidan tuzilgan savol:**\n\n{response.text}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Yangi savol olish", callback_data="ai_quiz")],
                [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_home")]
            ])
        )
    except Exception as e:
        logging.error(f"Gemini Quiz error: {e}")
        await callback.message.edit_text("⚠️ Savol yaratishda xatolik yuz berdi.", reply_markup=main_menu())

# --- 3. KUN IBORASI (Daily Idiom) ---
@dp.callback_query(F.data == "daily_idiom")
async def get_daily_idiom(callback: CallbackQuery):
    await callback.answer("Ibora qidirilmoqda...")
    
    prompt = (
        "Provide one interesting and useful English idiom. "
        "Explain its meaning in Uzbek and give an example sentence in English with Uzbek translation."
    )
    
    try:
        response = gemini_model.generate_content(prompt)
        await callback.message.edit_text(
            f"💡 **Kun iborasi (Idiom):**\n\n{response.text}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Boshqa ibora", callback_data="daily_idiom")],
                [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_home")]
            ])
        )
    except Exception as e:
        logging.error(f"Gemini Idiom error: {e}")
        await callback.message.edit_text("⚠️ Xatolik yuz berdi.", reply_markup=main_menu())

# --- 4. SHARH QOLDIRISH ---
@dp.callback_query(F.data == "feedback")
async def ask_feedback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(BotStates.waiting_feedback)
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="back_home")]
    ])
    await callback.message.edit_text(
        "✍️ **Bot haqidagi fikr yoki taklifingizni yozib yuboring:**",
        reply_markup=keyboard
    )

@dp.message(BotStates.waiting_feedback)
async def receive_feedback(message: Message, state: FSMContext):
    user_info = message.from_user.full_name
    username = f"@{message.from_user.username}" if message.from_user.username else "Usernamelar yo'q"
    feedback = message.text
    
    logging.info(f"Yangi Sharh [{user_info} - {username}]: {feedback}")
    
    await state.clear()
    await message.answer(
        "✅ **Rahmat! Sharhingiz qabul qilindi.**",
        reply_markup=main_menu()
    )

# --- RENDER WEB SERVER ---
async def handle(request):
    return web.Response(text="Super AI English Bot is Active!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Web server started on port {port}")

async def main():
    await web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
