import logging
from aiogram import Bot, Dispatcher, executor, types

# Sizning yangi tokeningiz
API_TOKEN = '8673930946:AAGfOL87ejN0vCKHrVQevYr4X_LrEV09YEw'

# Loglarni sozlash (xatoliklarni ko'rib turish uchun)
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Salom! Ingliz tili botingiz Render-da muvaffaqiyatli ishga tushdi! 🚀")

@dp.message_handler(commands=['help'])
async def help_cmd(message: types.Message):
    await message.answer("Ushbu bot ingliz tili savollari uchun tayyorlanmoqda.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
