import os
import random
import logging
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# ===== گرفتن توکن از Railway =====
TOKEN = os.getenv("TELEGRAM_TOKEN")

# ===== لاگ =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== دیتابیس =====
conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")
conn.commit()

def add_user(user_id):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()

def get_users():
    cursor.execute("SELECT user_id FROM users")
    return [row[0] for row in cursor.fetchall()]

# ===== منو =====
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🌙 متن شب", callback_data="night"),
         InlineKeyboardButton("🌿 متن زندگی", callback_data="life")],
        [InlineKeyboardButton("🤖 چت AI", callback_data="ai")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== استارت =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    add_user(user_id)

    await update.message.reply_text(
        "👋 خوش اومدی!\nیکی انتخاب کن:",
        reply_markup=main_menu()
    )

# ===== متن‌ها =====
night_texts = [
    "🌙 شب مهتابی...",
    "🌊 صدای موج...",
    "🌙 دلم تنگه..."
]

life_texts = [
    "🌿 زندگی ادامه داره",
    "☀️ لبخند بزن",
    "🌱 قوی باش"
]

# ===== دکمه‌ها =====
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "night":
        await query.edit_message_text(
            random.choice(night_texts),
            reply_markup=main_menu()
        )

    elif query.data == "life":
        await query.edit_message_text(
            random.choice(life_texts),
            reply_markup=main_menu()
        )

    elif query.data == "ai":
        context.user_data["ai"] = True
        await query.edit_message_text("🤖 سوالتو بپرس:")

# ===== چت AI ساده =====
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("ai"):
        text = update.message.text

        # فعلاً ساده (بعداً میشه وصل کرد به API واقعی)
        reply = f"🤖 جواب:\n{text[::-1]}"

        await update.message.reply_text(reply)

# ===== اجرای ربات =====
def main():
    if not TOKEN:
        raise ValueError("❌ TELEGRAM_TOKEN تنظیم نشده!")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))

    print("🚀 ربات اجرا شد")
    app.run_polling()

if __name__ == "__main__":
    main()
