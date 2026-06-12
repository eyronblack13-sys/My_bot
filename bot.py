import telebot
from telebot import types
import random
import threading
import time

TOKEN = "8923966527:AAF7yAKvyJpyq2WZjZYuxr-FBkLmZE05wOE"
SPONSOR_CHANNEL = "@CherikZone"

bot = telebot.TeleBot(TOKEN)

# -------------------------
# Check membership
# -------------------------
def is_member(user_id):
    try:
        member = bot.get_chat_member(SPONSOR_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# -------------------------
# Delete message after 5 seconds
# -------------------------
def delete_after_5(chat_id, message_id):
    time.sleep(5)
    try:
        bot.delete_message(chat_id, message_id)
        print("MESSAGE DELETED")
    except Exception as e:
        print("DELETE ERROR:", e)

# -------------------------
# Save videos from archive channel
# -------------------------
@bot.channel_post_handler(content_types=['video'])
def save_video(message):
    try:
        file_id = message.video.file_id
        with open("videos.txt", "a") as f:
            f.write(file_id + "\n")
        print("Video Saved")
    except Exception as e:
        print("SAVE ERROR:", e)

# -------------------------
# START
# -------------------------
@bot.message_handler(commands=['start'])
def start(message):
    if not is_member(message.from_user.id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("📢 کانال اسپانسر")
        markup.row("🔄 بررسی عضویت")

        bot.send_message(
            message.chat.id,
            "🔒 برای استفاده از ربات ابتدا عضو کانال اسپانسر شوید.",
            reply_markup=markup
        )
        return

    show_menu(message.chat.id)

# -------------------------
# MENU
# -------------------------
def show_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🔞 فیلم")
    markup.row("📢 کانال اسپانسر")

    bot.send_message(
        chat_id,
        "🎬 Movie Hub\n👇 انتخاب کن",
        reply_markup=markup
    )

# -------------------------
# HANDLER
# -------------------------
@bot.message_handler(func=lambda m: True)
def handler(message):
    text = message.text

    if text == "📢 کانال اسپانسر":
        bot.send_message(message.chat.id, "https://t.me/CherikZone")
        return

    if text == "🔄 بررسی عضویت":
        if is_member(message.from_user.id):
            bot.send_message(message.chat.id, "✅ تایید شد")
            show_menu(message.chat.id)
        else:
            bot.send_message(message.chat.id, "❌ هنوز عضو نیستی")
        return

    if text == "🔞 فیلم":
        try:
            with open("videos.txt", "r") as f:
                videos = f.read().splitlines()

            if not videos:
                bot.send_message(message.chat.id, "❌ فیلمی موجود نیست")
                return

            file_id = random.choice(videos)

            sent = bot.send_video(message.chat.id, file_id)

            msg_id = sent.message_id

            bot.send_message(
                message.chat.id,
                "⏳ فیلم ارسال شد\n⚠️ این فیلم بعد از ۵ ثانیه حذف خواهد شد"
            )

            threading.Thread(
                target=delete_after_5,
                args=(message.chat.id, msg_id),
                daemon=True
            ).start()

        except Exception as e:
            bot.send_message(message.chat.id, "❌ خطا در ارسال فیلم")
            print("ERROR:", e)

# -------------------------
# RUN BOT
# -------------------------
print("Bot is running...")

bot.infinity_polling(
    skip_pending=True,
    timeout=10,
    long_polling_timeout=5
)
