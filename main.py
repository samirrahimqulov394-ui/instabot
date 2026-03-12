from PIL import Image, ImageDraw, ImageFont
import io

# Sertifikat yasash funksiyasi
def create_certificate(name, score):
    # 1. Oddiy oq rasm yaratamiz (yoki tayyor shablon rasm ishlatish mumkin)
    # Hozircha oddiy ko'k ramkali sertifikat yaratamiz
    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # Ramka chizamiz
    draw.rectangle([20, 20, 780, 580], outline=(0, 102, 204), width=10)
    
    # Matnlarni yozamiz
    # Eslatma: Shrift fayli bo'lmasa, standart shrift ishlatiladi
    draw.text((400, 150), "SERTIFIKAT", fill=(0, 102, 204), anchor="mm", font_size=60)
    draw.text((400, 250), "Ushbu hujjat egasi:", fill=(0, 0, 0), anchor="mm", font_size=25)
    draw.text((400, 320), name.upper(), fill=(255, 0, 0), anchor="mm", font_size=45)
    draw.text((400, 400), f"Ingliz tili testidan {score}% natija qayd etdi", fill=(0, 0, 0), anchor="mm", font_size=25)
    draw.text((400, 500), "Tabriklaymiz!", fill=(34, 139, 34), anchor="mm", font_size=30)

    # Rasmni xotiraga (buffer) saqlaymiz
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

# Test tugagan joyda (check_ans ichida) natijani tekshiramiz:
@dp.callback_query(F.data.startswith("ans_"))
async def handle_finish(callback: types.CallbackQuery):
    uid = callback.from_user.id
    # ... (oldingi kod: natijani hisoblash)
    score_percent = (user_data[uid]['score'] / user_data[uid]['total']) * 100
    
    if score_percent >= 70:
        await callback.message.answer("Ajoyib! Natijangiz yuqori. Sertifikat tayyorlanmoqda... ⏳")
        cert_file = create_certificate(user_data[uid]['name'], score_percent)
        await bot.send_photo(
            chat_id=uid, 
            photo=types.BufferedInputFile(cert_file.read(), filename="certificate.png"),
            caption=f"Tabriklaymiz, {user_data[uid]['name']}! Mana sizning sertifkatingiz! 🏆"
        )
    else:
        await callback.message.answer(f"Test tugadi. Natijangiz: {score_percent}%. Sertifikat olish uchun 70% dan yuqori ball to'plang! 💪")
