import logging
from aiogram import Bot, Dispatcher, executor, types

# Sizning yangi tokeningiz shu yerda:
API_TOKEN = '8673930946:AAGfOL87ejN0vCKHrVQevYr4X_LrEV09YEw'

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Botni ishga tushirish
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Salom! Ingliz tili botingiz yangi tokenda ishlamoqda! 🚀")

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply("Bu bot ingliz tili savollarini o'rganish uchun mo'ljallangan.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
