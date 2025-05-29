import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN, ADMIN_ID, VIP_CHANNEL_ID, CARD_NUMBER
from database import *
from datetime import datetime
import threading
import time

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    text = f"""👋 Salom! Obunani to‘lash uchun kartamiz:

💳 {CARD_NUMBER}

✅ To‘lovdan so‘ng chekni shu yerga yuboring."""
    bot.send_message(message.chat.id, text)

@bot.message_handler(content_types=['photo'])
def handle_check(message):
    user_id = message.from_user.id
    caption = f"🧾 {user_id} dan chek keldi. Necha oylik obuna berilsin?"
    markup = InlineKeyboardMarkup()
    for m in [1, 3, 6, 12]:
        markup.add(InlineKeyboardButton(f"{m} oy", callback_data=f"confirm_{user_id}_{m}"))
    markup.add(InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"))
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_subscription(call):
    _, user_id, months = call.data.split("_")
    user_id, months = int(user_id), int(months)

    expire = extend_subscription(user_id, months)
    try:
        bot.send_message(user_id, f"✅ Obunangiz {months} oyga faollashtirildi.\n📅 Tugash vaqti: {expire.date()}")
        bot.send_message(VIP_CHANNEL_ID, f"/invite {user_id}")
        bot.send_message(call.message.chat.id, "✅ Obuna faollashtirildi va foydalanuvchi kanalga qo‘shildi.")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"⚠️ Xatolik: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def cancel_handler(call):
    bot.answer_callback_query(call.id, "Bekor qilindi.")

def monitor_subscriptions():
    while True:
        now = datetime.now()
        for user_id, exp in get_users():
            expire_date = datetime.fromisoformat(exp)
            if (expire_date - now).days == 1:
                try:
                    bot.send_message(user_id, "📅 Obunangiz tugashiga 1 kun qoldi. Iltimos, uzaytiring.")
                except:
                    pass
            elif now > expire_date:
                try:
                    bot.send_message(user_id, "❌ Obunangiz muddati tugadi. Kanalga kirish cheklaydi.")
                    bot.ban_chat_member(VIP_CHANNEL_ID, user_id)
                    delete_subscription(user_id)
                except:
                    pass
        time.sleep(3600)

threading.Thread(target=monitor_subscriptions, daemon=True).start()

bot.infinity_polling()