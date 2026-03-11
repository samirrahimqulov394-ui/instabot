import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from flask import Flask
from threading import Thread

# Sozlamalar
TOKEN = "8742866578:AAHt_zj3SZtvFwrBzxnjjuxMehVUlHEPbNY"
bot = Bot(token=TOKEN)
dp = Dispatcher()
app = Flask('')

# 1. Darajalar uchun Inline tugmalar yasash funksiyasi
def get_levels_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="A1 (Boshlang'ich)", callback_data="level_A1"),
        types.InlineKeyboardButton(text="B1 (O'rta)", callback_data="level_B1")
    )
    builder.row(
        types.InlineKeyboardButton(text="C1 (Professional)", callback_data="level_C1")
    )
    return builder.as_markup()

@app.route('/')
def home(): return "Bot Active!"

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 2. Start bosilganda darajani so'rash
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        f"Salom {message.from_user.first_name}!\n"
        "Botga xush kelibsiz. Testni boshlash uchun darajangizni tanlang:",
        reply_markup=get_levels_keyboard()
    )

# 3. Tugma bosilganda (CallbackQuery) testni yuborish
@dp.callback_query(F.data.startswith("level_"))
async def send_test(callback: types.CallbackQuery):
    level = callback.data.split("_")[1] # A1, B1 yoki C1 ni ajratib oladi
    
    if level == "A1":
        test_text = "🟢 A1 darajasi uchun test:\n\n1. I ___ a student.\nA) am\nB) is\nC) are"
    elif level == "B1":
        test_text = "🟡 B1 darajasi uchun test:\n\n1. If I ___ more time, I would learn Spanish.\nA) have\nB) had\nC) will have"
    elif level == "C1":
        test_text = "🔴 C1 darajasi uchun test:\n\n1. Hardly ___ the office when the phone rang.\nA) I had left\nB) had I left\nC) I left"

    # Eski xabarni tahrirlash (tugmalarni yo'qotib, testni chiqarish)
    await callback.message.edit_text(text=test_text)
    # Bildirishnoma (ekranning tepasida chiqadi)
    await callback.answer(f"Siz {level} darajasini tanladingiz")

async def main_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    Thread(target=run_http_server).start()
    asyncio.run(main_bot())
