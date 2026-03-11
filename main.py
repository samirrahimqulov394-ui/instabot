import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from flask import Flask
from threading import Thread

# 1. Botni sozlash
TOKEN = "8742866578:AAHt_zj3SZtvFwrBzxnjjuxMehVUlHEPbNY"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# 2. Render Port xatosini yo'qotish uchun kichik server
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run_http_server():
    # Render avtomatik beradigan PORTni olamiz, bo'lmasa 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 3. Bot buyruqlari
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(f"Salom {message.from_user.first_name}! Renderda muvaffaqiyatli ishga tushdim! ✅")

async def main_bot():
    print("Bot polling boshlandi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Serverni alohida oqimda (thread) yurgizamiz
    Thread(target=run_http_server).start()
    
    # Botni asosiy oqimda ishga tushiramiz
    asyncio.run(main_bot())
