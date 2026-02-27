import telebot
import yt_dlp
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

# 1. Render o'chib qolmasligi uchun (Port binding)
def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()
threading.Thread(target=run_dummy_server, daemon=True).start()

# 2. Bot sozlamalari
BOT_TOKEN = "8777776298:AAFJMLINXKvAtC-cmE-7GzpZ78bhVpONwdc"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Men tayyorman. 🚀\nInstagram yoki YouTube linkini yuboring.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if "http" in url:
        msg = bot.reply_to(message, "Yuklanmoqda... ⏳")
        file_path = f"video_{message.chat.id}.mp4"
        
        # Eng yengil formatda yuklash sozlamalari
        ydl_opts = {
            'format': 'best[ext=mp4]/best', # Faqat MP4 format
            'outtmpl': file_path,
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4'
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open(file_path, 'rb') as video:
                bot.send_video(message.chat.id, video)
            
            os.remove(file_path)
            bot.delete_message(message.chat.id, msg.message_id)
            
        except Exception as e:
            bot.edit_message_text(f"Xatolik: Video juda katta yoki profil yopiq.", message.chat.id, msg.message_id)
            if os.path.exists(file_path): os.remove(file_path)
    else:
        bot.reply_to(message, "Iltimos, link yuboring.")

bot.polling(none_stop=True)
