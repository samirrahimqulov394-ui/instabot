import logging
from aiogram import Bot, Dispatcher, executor, types

# Bot tokeningiz joyida
API_TOKEN = '8742866578:AAHt_zj3SZtvFwrBzxnjjuxMehVUlHEPbNY'

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
