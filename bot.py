import os
import random
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# ==================== متون ====================
JOKES = [ ... ]  # لیست جوک‌هاتون همان قبلی بماند (کوتاه کردم برای خوانایی)

NIGHT_TEXTS = [
    "🌙 شب مهتابی، لب دریا، صدای امواج...\nکاش کنارم بودی تا این لحظه رو باهم حس کنیم 💫",
    "🌊 شب‌هایی که ماه روی آب می‌تابه و دلم برای یه نفر تنگ میشه...",
    "🌙 لب دریا نشستم، باد موهامو به هم ریخت. فکر کردم به تو...",
]

LIFE_TEXTS = [
    "🌿 زندگی یعنی هر روز یه شروع تازه\nنفس بکش، لبخند بزن، ادامه بده 💚",
    "☀️ مهربونی کن، حتی وقتی کسی نمیبینه. دنیا به مهربون‌ها نیاز داره 🤍",
]

RESPECT_TEXTS = [
    "🤝 ادب نشونه بزرگیه، نه ضعف\nبا احترام حرف بزن، با احترام گوش بده 🌟",
    "👑 بزرگ‌ترین قدرت آدم اینه که بدون توهین حرفشو بزنه 💎",
]

LOVE_TEXTS = [
    "❤️ عشق یعنی وقتی اسمشو میبینی بی‌اختیار لبخند میزنی 🌹",
    "💕 خاطره‌های خوب هیچ وقت پاک نمیشن، فقط محو میشن 🌸",
]

LONELY_TEXTS = ["😢 روزهای تنها سخته ولی یادت باشه، فردا همیشه بهتره 🌙"]
NOVEL_TEXTS = ["📖 رمان خوندن یعنی توی هزار تا زندگی زندگی کردی 🌟"]
CITY_TEXTS = ["🏙️ شهر شبا قشنگه وقتی چراغا روشنن و خیابونا خلوت 🌃"]
FUN_TEXTS = ["🎉 سرگرمی یعنی بیخیال همه چیز بشی و فقط لذت ببری 🎊"]

def get_random_text(category: str) -> str:
    texts_map = {
        "night": NIGHT_TEXTS, "life": LIFE_TEXTS, "respect": RESPECT_TEXTS,
        "love": LOVE_TEXTS, "lonely": LONELY_TEXTS, "novel": NOVEL_TEXTS,
        "city": CITY_TEXTS, "fun": FUN_TEXTS, "joke": JOKES
    }
    texts = texts_map.get(category, JOKES)
    return random.choice(texts)


# ==================== کیبورد اصلی ====================
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🌙 شب‌های مهتابی", callback_data="menu_night"),
         InlineKeyboardButton("🌿 موضوعات زندگی", callback_data="menu_life")],
        [InlineKeyboardButton("🤝 ادب و احترام", callback_data="menu_respect"),
         InlineKeyboardButton("❤️ خاطرات عشق", callback_data="menu_love")],
        [InlineKeyboardButton("😂 خنده و شوخی", callback_data="menu_joke"),
         InlineKeyboardButton("🎉 سرگرمی", callback_data="menu_fun")],
        [InlineKeyboardButton("📚 بیشتر ➡️", callback_data="menu_second"),
         InlineKeyboardButton("🎲 یه متن تصادفی", callback_data="menu_random")],
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== هندلر دکمه‌ها (جدید و مطابق درخواستت) ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    title = ""
    text = ""
    footer_emoji = ""   # ایموجی پایین پیام

    if data == "menu_night":
        title = "🌙 شب‌های مهتابی"
        text = get_random_text("night")
        footer_emoji = "🌕✨"

    elif data == "menu_life":
        title = "🌿 موضوعات زندگی"
        text = get_random_text("life")
        footer_emoji = "🌱💚"

    elif data == "menu_respect":
        title = "🤝 ادب و احترام"
        text = get_random_text("respect")
        footer_emoji = "🙏👑"

    elif data == "menu_love":
        title = "❤️ خاطرات عشق"
        text = get_random_text("love")
        footer_emoji = "💖🌹"

    elif data == "menu_joke":
        title = "😂 خنده و شوخی"
        text = get_random_text("joke")
        footer_emoji = "🤣✨"

    elif data == "menu_fun":
        title = "🎉 سرگرمی"
        text = get_random_text("fun")
        footer_emoji = "🎊🎉"

    elif data == "menu_lonely":
        title = "😢 روزهای تنها"
        text = get_random_text("lonely")
        footer_emoji = "🌙😌"

    elif data == "menu_novel":
        title = "📖 رمان"
        text = get_random_text("novel")
        footer_emoji = "📚✨"

    elif data == "menu_city":
        title = "🏙️ شهر شب"
        text = get_random_text("city")
        footer_emoji = "🌃✨"

    elif data == "menu_random":
        title = "🎲 متن تصادفی"
        text = get_random_text(random.choice(["night","life","respect","love","joke","fun"]))
        footer_emoji = "⭐🎲"

    elif data == "menu_second":
        # منوی دوم
        keyboard = [
            [InlineKeyboardButton("😢 روزهای تنها", callback_data="menu_lonely"),
             InlineKeyboardButton("📖 رمان", callback_data="menu_novel")],
            [InlineKeyboardButton("🏙️ شهری بازی", callback_data="menu_city"),
             InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_main")],
        ]
        await query.edit_message_text(
            "📚 **منوی بیشتر:**\n\nدسته مورد علاقت رو انتخاب کن ✨",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    elif data == "back_main":
        await start(update, context)  # بازگشت به استارت
        return

    else:
        title = "❓ گزینه نامشخص"
        text = "این بخش هنوز تکمیل نشده است."
        footer_emoji = "❓"

    # ساخت پیام نهایی با ایموجی در پایین
    final_text = f"**{title}**\n\n{text}\n\n{footer_emoji}"

    # ارسال پیام جدید در پایین چت + منوی اصلی
    await query.message.reply_text(
        text=final_text,
        reply_markup=main_menu_keyboard(),
        parse_mode="Markdown"
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start"""
    text = "👋 سلام! خوش اومدی 🌟\n\nیه موضوع انتخاب کن:"
    await update.message.reply_text(text, reply_markup=main_menu_keyboard())


def main():
    if not TELEGRAM_TOKEN:
        logger.error("❌ توکن تلگرام پیدا نشد!")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("✅ ربات با موفقیت راه‌اندازی شد!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
