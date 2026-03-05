import logging
from aiogram import Bot, Dispatcher, executor, types

# Bot tokeningiz joyida
API_TOKEN = '8673930946:AAGfOL87ejN0vCKHrVQevYr4X_LrEV09YEw'

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcher obyektlari
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Bu yerda botingiz ishga tushganini tasdiqlaydi
    await message.reply("Salom! Ingliz tili botingiz Render-da muvaffaqiyatli ishga tushdi! ✅\n\nSavollarni boshlaymizmi?")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
