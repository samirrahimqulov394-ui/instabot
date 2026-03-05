import logging
from aiogram import Bot, Dispatcher, executor, types

# Sizning tokeningiz joylandi
API_TOKEN = '8673930946:AAGfOL87ejN0vCKHrVQevYr4X_LrEV09YEw'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Salom! Ingliz tili botingiz nihoyat ishga tushdi! ✅")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
