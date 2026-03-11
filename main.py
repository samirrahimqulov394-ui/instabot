import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from flask import Flask
from threading import Thread

# 1. Telegram Bot sozlamalari
TOKEN = os.getenv("BOT_TOKEN") # GitHub Secrets yoki Render Environment'dan oladi
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 2. Render uchun kichik Web Server (Port xatoligini oldini olish uchun)
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 3. Bot komandalari
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    await message.answer(f"Salom {message.from_user.full_name}! Bot Renderda muvaffaqiyatli ishga tushdi.")

async def main():
    # HTTP serverni alohida oqimda ishga tushiramiz
    Thread(target=run_http_server).start()
    
    # Botni ishga tushiramiz
    print("Bot polling rejimida ishlamoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
