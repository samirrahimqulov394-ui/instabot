import telebot
import yt_dlp
import os
import http.server
import threading

# 1. Render o'chirib qo'ymasligi uchun kichik server
def dummyserver():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot is running!")

    server = http.server.HTTPServer(('0.0.0.0', 10000), Handler)
    server.serve_forever()

threading.Thread(target=dummyserver, daemon=True).start()

# 2. Bot qismi
BOT_TOKEN = "8777776298:AAFJMLINXKvAtC-cmE-7GzpZ78bhVpONwdc"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom! Endi bot barqaror ishlaydi. Instagram, YouTube yoki TikTok linkini yuboring! 🚀")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    if any(site in url for site in ["instagram.com", "youtube.com", "youtu.be", "tiktok.com"]):
        msg = bot.reply_to(message, "Video yuklanyapti... ⏳")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open('video.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video)
            
            os.remove('video.mp4')
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            bot.reply_to(message, "Xatolik! Video olingan sayt profilini yoki havola to'g'riligini tekshiring.")
    else:
        bot.reply_to(message, "Iltimos, video havolasini yuboring.")

bot.polling()
