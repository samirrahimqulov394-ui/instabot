import os
import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from flask import Flask
from threading import Thread

# SOZLAMALAR
TOKEN = "8742866578:AAHt_zj3SZtvFwrBzxnjjuxMehVUlHEPbNY"
bot = Bot(token=TOKEN)
dp = Dispatcher()
app = Flask('')

# SAVOLLAR BAZASI (Bu yerga istalgancha savol qo'shing)
QUESTIONS = {
    "A1": [
        {"q": "I ___ a student.", "o": ["am", "is", "are"], "c": "am"},
        {"q": "She ___ to school every day.", "o": ["go", "goes", "going"], "c": "goes"},
        {"q": "___ you like pizza?", "o": ["Do", "Does", "Are"], "c": "Do"},
        {"q": "We ___ friends.", "o": ["is", "am", "are"], "c": "are"},
        {"q": "This is ___ apple.", "o": ["a", "an", "the"], "c": "an"},
    ],
    "B1": [
        {"q": "If I ___ you, I would stay home.", "o": ["am", "was", "were"], "c": "were"},
        {"q": "I haven't seen him ___ years.", "o": ["for", "since", "during"], "c": "for"},
        {"q": "She's interested ___ history.", "o": ["at", "in", "on"], "c": "in"},
    ],
    "C1": [
        {"q": "Hardly ___ started when the phone rang.", "o": ["I had", "had I", "I have"], "c": "had I"},
        {"q": "I'd rather you ___ that.", "o": ["don't do", "didn't do", "not do"], "c": "didn't do"},
    ]
}

# Foydalanuvchi sessiyasi
user_sessions = {}

@app.route('/')
def home(): return "Bot is Online"

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# 1. Start: Daraja tanlash
@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    kb = InlineKeyboardBuilder()
    for lvl in QUESTIONS.keys():
        kb.button(text=f"🎓 {lvl}", callback_data=f"set_lvl_{lvl}")
    kb.adjust(1)
    await message.answer("Xush kelibsiz! Imtihon darajasini tanlang:", reply_markup=kb.as_markup())

# 2. Savollar sonini tanlash
@dp.callback_query(F.data.startswith("set_lvl_"))
async def choose_qty(callback: types.CallbackQuery):
    lvl = callback.data.split("_")[2]
    kb = InlineKeyboardBuilder()
    # Savollar bazasidagi bor miqdordan oshib ketmasligi kerak
    options = [5, 10, 15, 20]
    for n in options:
        kb.button(text=f"📝 {n} ta", callback_data=f"set_qty_{lvl}_{n}")
    kb.adjust(2)
    await callback.message.edit_text(f"Siz {lvl} darajasini tanladingiz. Nechta savol yechmoqchisiz?", reply_markup=kb.as_markup())

# 3. Testni tayyorlash
@dp.callback_query(F.data.startswith("set_qty_"))
async def init_test(callback: types.CallbackQuery):
    _, _, lvl, qty = callback.data.split("_")
    qty = int(qty)
    
    # Savollarni aralashtirib berish (shuffled)
    all_q = QUESTIONS[lvl].copy()
    random.shuffle(all_q)
    selected_q = all_q[:qty]
    
    user_sessions[callback.from_user.id] = {
        "questions": selected_q,
        "current_idx": 0,
        "score": 0,
        "total": len(selected_q),
        "lvl": lvl
    }
    await send_next_question(callback.message, callback.from_user.id)

# 4. Savolni chiqarish
async def send_next_question(message, user_id):
    session = user_sessions[user_id]
    idx = session["current_idx"]
    
    if idx < session["total"]:
        q_data = session["questions"][idx]
        kb = InlineKeyboardBuilder()
        # Variantlarni ham aralashtiramiz
        opts = q_data["o"].copy()
        random.shuffle(opts)
        
        for opt in opts:
            kb.button(text=opt, callback_data=f"ans_{opt}")
        kb.adjust(1)
        
        text = f"📊 Daraja: {session['lvl']} | Savol: {idx+1}/{session['total']}\n\n{q_data['q']}"
        await message.edit_text(text, reply_markup=kb.as_markup())
    else:
        # Final natija
        score = session['score']
        total = session['total']
        percent = (score / total) * 100
        result_text = (
            f"🏁 **Imtihon tugadi!**\n\n"
            f"✅ To'g'ri javoblar: {score}\n"
            f"❌ Xato javoblar: {total - score}\n"
            f"🏆 Natija: {percent:.1f}%\n\n"
        )
        if percent >= 80: result_text += "Ajoyib! Siz bu darajani juda yaxshi bilasiz. 🔥"
        else: result_text += "Yana biroz o'qishingiz kerak. 📚"
        
        kb = InlineKeyboardBuilder()
        kb.button(text="Qayta boshlash 🔄", callback_data="restart")
        await message.edit_text(result_text, reply_markup=kb.as_markup())

# 5. Javobni tekshirish
@dp.callback_query(F.data.startswith("ans_"))
async def handle_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_sessions: return
    
    user_ans = callback.data.split("_")[1]
    session = user_sessions[user_id]
    correct_ans = session["questions"][session["current_idx"]]["c"]
    
    if user_ans == correct_ans:
        session["score"] += 1
        await callback.answer("To'g'ri! ✅", show_alert=False)
    else:
        await callback.answer(f"Xato! ❌ To'g'ri javob: {correct_ans}", show_alert=True)
        
    session["current_idx"] += 1
    await send_next_question(callback.message, user_id)

@dp.callback_query(F.data == "restart")
async def restart_quiz(callback: types.CallbackQuery):
    await start_cmd(callback.message)

async def main():
    Thread(target=run_http_server).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
