import telebot
from telebot import types
import instaloader
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

API_TOKEN = '8777776298:AAFJMLINXKvAtC-cmE-7GzpZ78bhVpONwdc'
bot = telebot.TeleBot(API_TOKEN)
L = instaloader.Instaloader()

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎬 Video yuklash", "ℹ️ Bot haqida")
    bot.send_message(message.chat.id, "Bot serverda yoniq! 🚀", reply_markup=markup)

@bot.message_handler(func=lambda message: "instagram.com" in message.text)
def handle_insta(message):
    msg = bot.reply_to(message, "Yuklanmoqda... ⏳")
    try:
        url = message.text.strip().split("/")
        shortcode = ""
        for i in range(len(url)):
            if url[i] in ['reels', 'p', 'reel'] and i+1 < len(url):
                shortcode = url[i+1].split('?')[0]
                break
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        bot.send_video(message.chat.id, post.video_url, caption="Tayyor! ✅")
        bot.delete_message(message.chat.id, msg.message_id)
    except:
        bot.edit_message_text("Xato! Profil yopiq bo'lishi mumkin.", message.chat.id, msg.message_id)

def start_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    start_bot()
