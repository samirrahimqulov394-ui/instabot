import telebot
import yt_dlp
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Render o'chirib qo'ymasligi uchun
def run_server():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()
threading.Thread(target=run_server, daemon=True).start()

BOT_TOKEN = "8777776298:AAFJMLINXKvAtC-cmE-7GzpZ78bhVpONwdc"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom! Men tayyorman. Link yuboring! 🚀")

@bot.message_handler(func=lambda message: True)
def download(message):
    url = message.text
    if "http" in url:
        sent_msg = bot.reply_to(message, "Yuklanyapti... ⏳")
        file_name = f"{message.chat.id}.mp4"
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': file_name,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open(file_name, 'rb') as video:
                bot.send_video(message.chat.id, video)
            
            os.remove(file_name)
            bot.delete_message(message.chat.id, sent_msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"Xato: Video juda katta yoki havola yopiq.", message.chat.id, sent_msg.message_id)
    else:
        bot.reply_to(message, "Iltimos, link yuboring!")

bot.polling(none_stop=True)
