import logging
from aiogram import Bot, Dispatcher, executor, types

# Bot tokeningiz
API_TOKEN = '8673930946:AAGfOL87ejN0vCKHrVQevYr4X_LrEV09YEw'

# Botni sozlash
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Savollar bazasi (namuna)
quiz_data = [
    {
        "question": "1. 'Apple' so'zining o'zbekcha ma'nosi nima?",
        "options": ["Nok", "Olma", "Uzum"],
        "correct": "Olma"
    },
    {
        "question": "2. Choose the correct verb: I ___ to school every day.",
        "options": ["go", "goes", "went"],
        "correct": "go"
    }
]

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Salom! Ingliz tili botiga xush kelibsiz.\nTestni boshlash uchun /test buyrug'ini yuboring.")

@dp.message_handler(commands=['test'])
async def start_quiz(message: types.Message):
    for item in quiz_data:
        # Har bir savol uchun tugmalar yaratamiz
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for option in item["options"]:
            keyboard.add(option)
            
        await message.answer(item["question"], reply_markup=keyboard)

@dp.message_handler(lambda message: any(q["options"] for q in quiz_data if message.text in q["options"]))
async def check_answer(message: types.Message):
    # Bu yerda javobni tekshirish logikasi (soddalashtirilgan)
    found = False
    for q in quiz_data:
        if message.text in q["options"]:
            if message.text == q["correct"]:
                await message.answer(f"To'g'ri! ✅")
            else:
                await message.answer(f"Xato. To'g'ri javob: {q['correct']} ❌")
            found = True
            break

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
