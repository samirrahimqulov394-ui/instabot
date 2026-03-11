import os
import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from flask import Flask
from threading import Thread

# TOKENS
BOT_TOKEN = "8742866578:AAHt_zj3SZtvFwrBzxnjjuxMehVUlHEPbNY"
PAYMENT_TOKEN = "398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
app = Flask('')

# SAVOLLAR (Demo uchun qisqa)
QUESTIONS = {
    "A1": [{"q": "I ___ a student.", "o": ["am", "is", "are"], "c": "am"}],
    "B1": [{"q": "He ___ to school.", "o": ["goes", "go", "going"], "c": "goes"}]
}

user_data = {}

@app.route('/')
def home(): return "Payment Bot is Live"

def run_http_server():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- START ---
@dp.message(CommandStart())
async def start(message: types.Message):
    user_data[message.from_user.id] = {"step": "name"}
    await message.answer("Xush kelibsiz! Ismingizni kiriting:")

@dp.message(lambda m: user_data.get(m.from_user.id, {}).get("step") == "name")
async def get_name(message: types.Message):
    uid = message.from_user.id
    user_data[uid] = {"name": message.text, "step": "quiz"}
    kb = InlineKeyboardBuilder()
    for lvl in QUESTIONS.keys(): kb.button(text=lvl, callback_data=f"lvl_{lvl}")
    await message.answer(f"Salom {message.text}, darajani tanlang:", reply_markup=kb.as_markup())

# --- TEST JARAYONI ---
@dp.callback_query(F.data.startswith("lvl_"))
async def start_quiz(callback: types.CallbackQuery):
    lvl = callback.data.split("_")[1]
    uid = callback.from_user.id
    q = QUESTIONS[lvl][0] # Demo: faqat 1-savol
    user_data[uid].update({"cur_q": q, "score": 0})
    
    kb = InlineKeyboardBuilder()
    for o in q["o"]: kb.button(text=o, callback_data=f"ans_{o}")
    await callback.message.edit_text(q["q"], reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("ans_"))
async def check_ans(callback: types.CallbackQuery):
    uid = callback.from_user.id
    ans = callback.data.split("_")[1]
    q = user_data[uid]["cur_q"]
    
    if ans == q["c"]:
        user_data[uid]["score"] += 1
        await callback.answer("To'g'ri! ✅")
    else:
        await callback.answer(f"Xato! ❌", show_alert=True)
    
    # Test tugagach to'lov taklif qilish
    kb = InlineKeyboardBuilder()
    kb.button(text="💎 VIP Testlarni sotib olish (10,000 so'm)", callback_data="buy_vip")
    await callback.message.edit_text(
        f"Test tugadi! Natijangiz: {user_data[uid]['score']}\n\n"
        f"Ko'proq va qiyinroq testlar uchun VIP paketni sotib oling:",
        reply_markup=kb.as_markup()
    )

# --- TO'LOV TIZIMI ---
@dp.callback_query(F.data == "buy_vip")
async def send_invoice(callback: types.CallbackQuery):
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="VIP Testlar To'plami",
        description="1000 ta professional test va tushuntirishlar",
        payload="vip_pack",
        provider_token=PAYMENT_TOKEN,
        currency="UZS",
        prices=[types.LabeledPrice(label="VIP Obuna", amount=1000000)], # 10,000 UZS
        start_parameter="pay"
    )

@dp.pre_checkout_query(lambda q: True)
async def pre_checkout(query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(F.successful_payment)
async def success(message: types.Message):
    await message.answer(f"Rahmat! 🎉 To'lov qabul qilindi. Endi siz VIP foydalanuvchisiz!")

async def main():
    Thread(target=run_http_server).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
