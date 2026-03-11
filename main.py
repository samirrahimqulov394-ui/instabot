import os
import asyncio
import sqlite3
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from flask import Flask
from threading import Thread

TOKEN = "8742866578:AAHt_zj3SZtvFwrBzxnjjuxMehVUlHEPbNY"
bot = Bot(token=TOKEN)
dp = Dispatcher()
app = Flask('')

# --- DATABASE QISMI ---
def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            full_name TEXT,
            best_score REAL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def save_user(user_id, name):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, full_name) VALUES (?, ?)", (user_id, name))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT full_name FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None

# --- TEST SAVOLLARI ---
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

user_sessions = {}

@app.route('/')
def home(): return "Bot Active with SQLite"

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT MANTIQI ---

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    user_name = get_user(message.from_user.id)
    
    if user_name:
        # Agar baza bo'lsa, ism so'ramaymiz
        await message.answer(f"Xush kelibsiz, {user_name}! Darajani tanlang:", reply_markup=get_levels_kb())
    else:
        # Birinchi marta kirgan bo'lsa
        user_sessions[message.from_user.id] = {"step": "get_name"}
        await message.answer("Xush kelibsiz! Ism-sharifingizni yuboring:")

@dp.message(lambda msg: user_sessions.get(msg.from_user.id, {}).get("step") == "get_name")
async def register_user(message: types.Message):
    name = message.text
    save_user(message.from_user.id, name) # Bazaga saqlash
    user_sessions[message.from_user.id] = {"name": name}
    await message.answer(f"Rahmat, {name}! Endi darajani tanlang:", reply_markup=get_levels_kb())

def get_levels_kb():
    kb = InlineKeyboardBuilder()
    for lvl in QUESTIONS.keys():
        kb.button(text=f"🎓 {lvl}", callback_data=f"lvl_{lvl}")
    kb.adjust(1)
    return kb.as_markup()

@dp.callback_query(F.data.startswith("lvl_"))
async def choose_qty(callback: types.CallbackQuery):
    lvl = callback.data.split("_")[1]
    user_sessions[callback.from_user.id]["lvl"] = lvl
    kb = InlineKeyboardBuilder()
    for n in [5, 10]:
        kb.button(text=f"{n} ta savol", callback_data=f"qty_{n}")
    await callback.message.edit_text(f"{lvl} darajasi tanlandi. Savol sonini tanlang:", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("qty_"))
async def start_test(callback: types.CallbackQuery):
    uid = callback.from_user.id
    qty = int(callback.data.split("_")[1])
    lvl = user_sessions[uid]["lvl"]
    
    q_list = QUESTIONS[lvl].copy()
    random.shuffle(q_list)
    
    user_sessions[uid].update({
        "qs": q_list[:qty], "cur": 0, "score": 0, "total": qty
    })
    await send_q(callback.message, uid)

async def send_q(message, uid):
    data = user_sessions[uid]
    if data["cur"] < data["total"]:
        q = data["qs"][data["cur"]]
        kb = InlineKeyboardBuilder()
        opts = q["o"].copy()
        random.shuffle(opts)
        for o in opts: kb.button(text=o, callback_data=f"ans_{o}")
        kb.adjust(1)
        await message.edit_text(f"Savol {data['cur']+1}/{data['total']}:\n\n{q['q']}", reply_markup=kb.as_markup())
    else:
        name = get_user(uid)
        res = (data['score'] / data['total']) * 100
        await message.edit_text(f"🏁 Test tugadi, {name}!\n✅ To'g'ri: {data['score']}\n🏆 Natija: {res:.1f}%")

@dp.callback_query(F.data.startswith("ans_"))
async def handle_ans(callback: types.CallbackQuery):
    uid = callback.from_user.id
    ans = callback.data.split("_")[1]
    data = user_sessions[uid]
    
    if ans == data["qs"][data["cur"]]["c"]:
        data["score"] += 1
        await callback.answer("To'g'ri! ✅")
    else:
        await callback.answer(f"Xato! ❌", show_alert=True)
        
    data["cur"] += 1
    await send_q(callback.message, uid)

async def main():
    init_db() # Bazani ishga tushirish
    Thread(target=run_http_server).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
