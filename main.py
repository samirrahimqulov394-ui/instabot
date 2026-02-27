import telebot
import yt_dlp
import os

# Botingiz tokni (Siz bergan token)
BOT_TOKEN = "8777776298:AAFJMLINXKvAtC-cmE-7GzpZ78bhVpONwdc"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom! Men Instagram, YouTube va TikTok videolarini yuklab beraman. Menga shunchaki havola (link) yuboring! 🚀")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    # Havolani tekshirish
    if any(site in url for site in ["instagram.com", "youtube.com", "youtu.be", "tiktok.com"]):
        msg = bot.reply_to(message, "Video tayyorlanyapti, iltimos kuting... ⏳")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
            'noplaylist': True,
            'quiet': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open('video.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video)
            
            # Faylni serverdan o'chirish (joy egallamasligi uchun)
            if os.path.exists('video.mp4'):
                os.remove('video.mp4')
            
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            bot.reply_to(message, f"Xato yuz berdi: Video yuklashda muammo bo'ldi. Profil yopiq emasligiga ishonch hosil qiling.")
    else:
        bot.reply_to(message, "Iltimos, faqat Instagram, YouTube yoki TikTok havolasini yuboring.")

bot.polling()
