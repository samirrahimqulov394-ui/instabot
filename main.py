import os
import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from flask import Flask
from threading import Thread

TOKEN = "8742866578:AAHt_zj3SZtvFwrBzxnjjuxMehVUlHEPbNY"
bot = Bot(token=TOKEN)
dp = Dispatcher()
app = Flask('')

# SAVOLLAR BAZASI (Professional ko'rinishda)
QUESTIONS = {
    "A1": [
        {"q": "I ___ a student.", "o": ["am", "is", "are"], "c": "am"},
        {"q": "She ___ to school every day.", "o": ["go", "goes", "going"], "c": "goes"},
        {"q": "___ you like pizza?", "o": ["Do", "Does", "Are"], "c": "Do"},
        {"q": "We ___ friends.", "o": ["is", "am", "are"], "c": "are"},
        {"q": "Look! It ___ raining.", "o": ["is", "am", "are"], "c": "is"},
    ],
    "B1": [
        {"q": "If I ___ more time, I would learn Spanish.", "o": ["have", "had", "will have"], "c": "had"},
        {"q": "I've been here ___ 3 hours.", "o": ["for", "since", "at"], "c": "for"},
    ]
}

user_data = {}

@app.route('/')
def home(): return "Professional Bot is Running"

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 1. Start - Ro'yxatga olishni boshlash
@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user_data[message.from_user.id] = {"step": "get_name"}
    await message.answer("Xush kelibsiz! Professional test tizimiga kirish uchun ism-sharifingizni yuboring:")

# 2. Ismni qabul qilish va darajani so'rash
@dp.message(lambda msg: user_data.get(msg.from_user.id, {}).get("step") == "get_name")
async def get_name(message: types.Message):
    user_data[message.from_user.id]["name"] = message.text
    user_data[message.from_user.id]["step"] = "choose_level"
    
    kb = InlineKeyboardBuilder()
    for lvl in QUESTIONS.keys():
        kb.button(text=f"🎓 {lvl}", callback_data=f"lvl_{lvl}")
    kb.adjust(1)
    
    await message.answer(f"Rahmat, {message.text}! Endi test darajasini tanlang:", reply_markup=kb.as_markup())

# 3. Savollar sonini tanlash
@dp.callback_query(F.data.startswith("lvl_"))
async def set_level(callback: types.CallbackQuery):
    lvl = callback.data.split("_")[1]
    user_data[callback.from_user.id]["lvl"] = lvl
    
    kb = InlineKeyboardBuilder()
    for n in [5, 10, 15]:
        kb.button(text=f"📝 {n} ta savol", callback_data=f"qty_{n}")
    kb.adjust(1)
    await callback.message.edit_text(f"Yaxshi, {lvl} darajasi. Nechta savol yechasiz?", reply_markup=kb.as_markup())

# 4. Testni boshlash
@dp.callback_query(F.data.startswith("qty_"))
async def start_quiz(callback: types.CallbackQuery):
    qty = int(callback.data.split("_")[1])
    uid = callback.from_user.id
    lvl = user_data[uid]["lvl"]
    
    all_q = QUESTIONS[lvl].copy()
    random.shuffle(all_q)
    
    user_data[uid].update({
        "questions": all_q[:qty],
        "current": 0,
        "score": 0,
        "total": qty,
        "step": "quiz"
    })
    await send_q(callback.message, uid)

async def send_q(message, uid):
    data = user_data[uid]
    idx = data["current"]
    
    if idx < len(data["questions"]):
        q = data["questions"][idx]
        kb = InlineKeyboardBuilder()
        opts = q["o"].copy()
        random.shuffle(opts)
        for o in opts:
            kb.button(text=o, callback_data=f"ans_{o}")
        kb.adjust(1)
        await message.edit_text(f"Savol {idx+1}/{data['total']}:\n\n{q['q']}", reply_markup=kb.as_markup())
    else:
        # Professional natija
        res = (data['score'] / data['total']) * 100
        await message.edit_text(
            f"📊 Natija: {user_data[uid]['name']}\n"
            f"✅ To'g'ri: {data['score']}\n"
            f"❌ Xato: {data['total'] - data['score']}\n"
            f"🏆 Ko'rsatkich: {res:.1f}%"
        )

# 5. Javobni tekshirish (Alert bilan)
@dp.callback_query(F.data.startswith("ans_"))
async def check(callback: types.CallbackQuery):
    uid = callback.from_user.id
    if uid not in user_data: return
    
    ans = callback.data.split("_")[1]
    data = user_data[uid]
    correct = data["questions"][data["current"]]["c"]
    
    if ans == correct:
        data["score"] += 1
        await callback.answer("To'g'ri! ✅")
    else:
        await callback.answer(f"Xato! ❌ To'g'ri javob: {correct}", show_alert=True)
    
    data["current"] += 1
    await send_q(callback.message, uid)

async def main():
    Thread(target=run_http_server).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
