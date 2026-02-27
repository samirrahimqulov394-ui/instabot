import telebot
import yt_dlp
import os
import http.server
import threading

# Render uchun kichik server
def dummyserver():
    class Handler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot ishlayapti!")
    server = http.server.HTTPServer(('0.0.0.0', 10000), Handler)
    server.serve_forever()

threading.Thread(target=dummyserver, daemon=True).start()

BOT_TOKEN = "8777776298:AAFJMLINXKvAtC-cmE-7GzpZ78bhVpONwdc"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Link yuboring, videoni yuklab beraman! 🚀")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    if "http" in url:
        msg = bot.reply_to(message, "Yuklash boshlandi... ⏳")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
            'no_warnings': True,
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
            bot.reply_to(message, "Xatolik! Link noto'g'ri yoki video juda katta.")
    else:
        bot.reply_to(message, "Iltimos, video linkini yuboring.")

bot.polling(none_stop=True)
