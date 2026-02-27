import telebot
import yt_dlp
import os

# Botingiz tokenni shu yerga qo'ying
BOT_TOKEN = "7917787498:AAEkL3R772x0o6M15vXN0o6M15vXN0o6M15" # O'zingiznikini qo'ying
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Salom! Men Instagram, YouTube va TikTok videolarini yuklab beraman. Menga havola (link) yuboring! 🚀")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    if "instagram.com" in url or "youtube.com" in url or "youtu.be" in url or "tiktok.com" in url:
        msg = bot.reply_to(message, "Video tayyorlanyapti, iltimos kuting... ⏳")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'video.mp4',
            'noplaylist': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            with open('video.mp4', 'rb') as video:
                bot.send_video(message.chat.id, video)
            
            os.remove('video.mp4') # Faylni o'chirish
            bot.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            bot.reply_to(message, f"Xato yuz berdi: {e}")
    else:
        bot.reply_to(message, "Iltimos, faqat Instagram, YouTube yoki TikTok havolasini yuboring.")

bot.polling()
