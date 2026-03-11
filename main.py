import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from flask import Flask
from threading import Thread

# TOKEN - o'zingizniki turibdi
TOKEN = "8742866578:AAHt_zj3SZtvFwrBzxnjjuxMehVUlHEPbNY"
bot = Bot(token=TOKEN)
dp = Dispatcher()
app = Flask('')

@app.route('/')
def home(): return "Bot Active!"

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Darajalar tugmasi
def get_levels_kb():
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="A1", callback_data="level_A1"))
    builder.row(types.InlineKeyboardButton(text="B1", callback_data="level_B1"))
    builder.row(types.InlineKeyboardButton(text="C1", callback_data="level_C1"))
    return builder.as_markup()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    # Bu xabar tugmalar bilan chiqishi shart!
    await message.answer(
        f"Salom {message.from_user.first_name}! Darajangizni tanlang:",
        reply_markup=get_levels_kb()
    )

@dp.callback_query(F.data.startswith("level_"))
async def level_selected(callback: types.CallbackQuery):
    level = callback.data.split("_")[1]
    await callback.message.edit_text(f"Siz {level} darajasini tanladingiz. Tayyormisiz?")
    await callback.answer()

async def main():
    Thread(target=run_http_server).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
