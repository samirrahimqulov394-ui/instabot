import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

# TOKENNI SHU YERGA QO'YDIK
TOKEN = "8742866578:AAHt_zj3SZtvFwrBzxnjjuxMehVUlHEPbNY"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(f"Salom {message.from_user.first_name}! Bot Render va GitHub orqali ishlamoqda! ✅")

@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"Siz yozdingiz: {message.text}")

async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi")
