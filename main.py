import os
import asyncio
import io
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from flask import Flask
from threading import Thread
from PIL import Image, ImageDraw

# TOKENS
BOT_TOKEN = "8742866578:AAHt_zj3SZtvFwrBzxnjjuxMehVUlHEPbNY"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = Flask('')

# SAVOLLAR (Buni ko'paytirishingiz mumkin)
QUESTIONS = {
    "A1": [
        {"q": "I ___ a student.", "o": ["am", "is", "are"], "c": "am"},
        {"q": "Apple is a ___.", "o": ["fruit", "car", "city"], "c": "fruit"}
    ],
    "B1": [
        {"q": "He ___ to school.", "o": ["goes", "go", "going"], "c": "goes"}
    ]
}

user_data = {}

@app.route('/')
def home(): return "Sertifikat Bot Active"

def run_http_server():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- SERTIFIKAT YASASH ---
def create_certificate(name, score):
    # Oq fonli rasm (800x600)
    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Ramka chizamiz
    draw.rectangle([20, 20, 780, 580], outline=(0, 50, 150), width=15)
    draw.rectangle([40, 40, 760, 560], outline=(200, 150, 50), width=5)
    
    # Matnlar (Shrift yuklamasdan, standart bilan)
    draw.text((400, 100), "TEST NATIJASI", fill=(0, 50, 150), anchor="mm")
    draw.text((400, 250), "Ushbu sertifikat egasi:", fill=(100, 100, 100), anchor="mm")
    draw.text((400, 320), name.upper(), fill=(0, 0, 0), anchor="mm")
    draw.text((400, 400), f"Natija: {score}%", fill=(0, 128, 0), anchor="mm")
    draw.text((400, 500), "Tabriklaymiz!", fill=(0, 50, 150), anchor="mm")

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

# --- BOT LOGIKASI ---
@dp.message(CommandStart())
async def start(message: types.Message):
    user_data[message.from_user.id] = {"step": "name"}
    await message.answer("Xush kelibsiz! Sertifikat olish uchun ismingizni kiriting:")

@dp.message(lambda m: user_data.get(m.from_user.id, {}).get("step") == "name")
async def get_name(message: types.Message):
    uid = message.from_user.id
    user_data[uid] = {"name": message.text, "step": "quiz"}
    kb = InlineKeyboardBuilder()
    for lvl in QUESTIONS.keys(): kb.button(text=lvl, callback_data=f"lvl_{lvl}")
    await message.answer(f"Salom {message.text}, darajani tanlang:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("lvl_"))
async def start_quiz(callback: types.CallbackQuery):
    lvl = callback.data.split("_")[1]
    uid = callback.from_user.id
    q_list = QUESTIONS[lvl]
    user_data[uid].update({"qs": q_list, "cur": 0, "score": 0, "total": len(q_list)})
    await send_q(callback.message, uid)

async def send_q(message, uid):
    data = user_data[uid]
    if data["cur"] < data["total"]:
        q = data["qs"][data["cur"]]
        kb = InlineKeyboardBuilder()
        for o in q["o"]: kb.button(text=o, callback_data=f"ans_{o}")
        await message.edit_text(q["q"], reply_markup=kb.as_markup())
    else:
        # TEST TUGADI
        score_percent = int((data['score'] / data['total']) * 100)
        await message.answer(f"Test tugadi! Natijangiz: {score_percent}%")
        
        if score_percent >= 50:
            await message.answer("Sertifikat tayyorlanmoqda... 🎓")
            cert_img = create_certificate(data['name'], score_percent)
            await bot.send_photo(
                chat_id=uid,
                photo=types.BufferedInputFile(cert_img.read(), filename="cert.png"),
                caption="Mana sizning sertifikatingiz! 🏆"
            )
        else:
            await message.answer("Sertifikat olish uchun 50% dan yuqori ball kerak. Qaytadan urinib ko'ring!")

@dp.callback_query(F.data.startswith("ans_"))
async def check_ans(callback: types.CallbackQuery):
    uid = callback.from_user.id
    ans = callback.data.split("_")[1]
    data = user_data[uid]
    
    if ans == data["qs"][data["cur"]]["c"]:
        data["score"] += 1
        await callback.answer("To'g'ri! ✅")
    else:
        await callback.answer("Xato! ❌")
        
    data["cur"] += 1
    await send_q(callback.message, uid)

async def main():
    Thread(target=run_http_server).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
