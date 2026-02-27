import telebot
from telebot import types
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

# 1. Render uchun server (Port xatosi bermasligi uchun)
def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()
threading.Thread(target=run_server, daemon=True).start()

# 2. Yangi Bot Tokeningiz
BOT_TOKEN = "8673329196:AAFl2edOLz9M7Rip0dihcbRsjsT542S16L0"
bot = telebot.TeleBot(BOT_TOKEN)

# 3. Test Savollari (Bu yerga xohlagancha savol qo'shishingiz mumkin)
questions = [
    {
        "q": "I ___ English every day.",
        "options": ["study", "studies", "studying", "studied"],
        "correct": "study"
    },
    {
        "q": "___ you like coffee?",
        "options": ["Does", "Do", "Are", "Is"],
        "correct": "Do"
    },
    {
        "q": "Choose the correct word: 'Bino'",
        "options": ["Car", "Building", "Tree", "Street"],
        "correct": "Building"
    }
]

user_data = {}

@bot.message_handler(commands=['start', 'test'])
def start_test(message):
    user_data[message.chat.id] = 0 # Savollarni 0-dan boshlash
    bot.send_message(message.chat.id, "Ingliz tili test botiga xush kelibsiz! 🎓")
    send_question(message)

def send_question(message):
    chat_id = message.chat.id
    q_index = user_data[chat_id]
    
    if q_index < len(questions):
        q = questions[q_index]
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for option in q["options"]:
            markup.add(option)
        
        bot.send_message(chat_id, f"Savol {q_index + 1}: {q['q']}", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Tabriklayman! Hamma savollarga javob berdingiz. 🎉\nQayta boshlash uchun /test buyrug'ini bosing.")

@bot.message_handler(func=lambda message: True)
def check_answer(message):
    chat_id = message.chat.id
    if chat_id in user_data:
        q_index = user_data[chat_id]
        if q_index < len(questions):
            correct_ans = questions[q_index]["correct"]
            
            if message.text == correct_ans:
                bot.send_message(chat_id, "To'g'ri! ✅")
            else:
                bot.send_message(chat_id, f"Xato! ❌ To'g'ri javob: {correct_ans}")
            
            user_data[chat_id] += 1
            send_question(message)

bot.polling(none_stop=True)
