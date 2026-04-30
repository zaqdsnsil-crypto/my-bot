import os
import random
import logging
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# ==================== متون ====================
JOKES = [ ... ]  # لیست کامل جوک‌هات رو اینجا بذار (همون قبلی)

NIGHT_TEXTS = ["🌙 شب مهتابی، لب دریا، صدای امواج...\nکاش کنارم بودی 💫", "🌊 شب‌هایی که ماه روی آب می‌تابه... 🤍"]
LIFE_TEXTS = ["🌿 زندگی یعنی هر روز یه شروع تازه 💚", "☀️ مهربونی کن، دنیا به مهربون‌ها نیاز داره 🤍"]
RESPECT_TEXTS = ["🤝 ادب نشونه بزرگیه 🌟", "👑 بدون توهین حرف بزن 💎"]
LOVE_TEXTS = ["❤️ عشق یعنی وقتی اسمشو می‌بینی لبخند میزنی 🌹", "💕 خاطره‌های خوب پاک نمیشن 🌸"]
LONELY_TEXTS = ["😢 روزهای تنها سخته ولی فردا بهتره 🌙"]
NOVEL_TEXTS = ["📖 رمان خوندن یعنی توی هزار تا زندگی زندگی کردی 🌟"]
CITY_TEXTS = ["🏙️ شهر شبا قشنگه وقتی چراغا روشنن 🌃"]
FUN_TEXTS = ["🎉 سرگرمی یعنی بیخیال همه چیز بشی 🎊"]

def get_random_text(category: str) -> str:
    texts_map = {
        "night": NIGHT_TEXTS, "life": LIFE_TEXTS, "respect": RESPECT_TEXTS,
        "love": LOVE_TEXTS, "lonely": LONELY_TEXTS, "novel": NOVEL_TEXTS,
        "city": CITY_TEXTS, "fun": FUN_TEXTS, "joke": JOKES
    }
    return random.choice(texts_map.get(category, JOKES))


def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("شب‌های مهتابی 🌙", callback_data="menu_night"),
         InlineKeyboardButton("موضوعات زندگی 🌿", callback_data="menu_life")],
        [InlineKeyboardButton("ادب و احترام 🤝", callback_data="menu_respect"),
         InlineKeyboardButton("خاطرات عشق ❤️", callback_data="menu_love")],
        [InlineKeyboardButton("خنده و شوخی 😂", callback_data="menu_joke"),
         InlineKeyboardButton("سرگرمی 🎉", callback_data="menu_fun")],
        [InlineKeyboardButton("➡️ بیشتر", callback_data="menu_second"),
         InlineKeyboardButton("یه متن تصادفی 🎲", callback_data="menu_random")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # همه گزینه‌های اصلی و فرعی → پیام جدید در پایین
    category_map = {
        "menu_night":    ("night",    "شب‌های مهتابی",     "🌕✨"),
        "menu_life":     ("life",     "موضوعات زندگی",    "🌱💚"),
        "menu_respect":  ("respect",  "ادب و احترام",      "🙏"),
        "menu_love":     ("love",     "خاطرات عشق",       "💖🌹"),
        "menu_joke":     ("joke",     "خنده و شوخی",      "🤣"),
        "menu_fun":      ("fun",      "سرگرمی",           "🎊"),
        "menu_lonely":   ("lonely",   "روزهای تنها",       "🌙😌"),
        "menu_novel":    ("novel",    "رمان",              "📚"),
        "menu_city":     ("city",     "شهری بازی",         "🌃"),
    }

    if data in category_map:
        cat, title, footer = category_map[data]
        text = get_random_text(cat)
        final_text = f"**{title}**\n\n{text}\n\n{footer}"

        await query.message.reply_text(
            text=final_text,
            reply_markup=main_menu_keyboard(),   # منوی اصلی همیشه بماند
            parse_mode="Markdown"
        )
        return

    # متن تصادفی
    if data == "menu_random":
        cat = random.choice(list(category_map.keys())[:-3])  # یکی از دسته‌ها
        cat_key = category_map[cat][0]
        title = "متن تصادفی"
        text = get_random_text(cat_key)
        final_text = f"**{title}**\n\n{text}\n\n⭐🎲"

        await query.message.reply_text(
            text=final_text,
            reply_markup=main_menu_keyboard(),
            parse_mode="Markdown"
        )
        return

    # منوی بیشتر
    if data == "menu_second":
        keyboard = [
            [InlineKeyboardButton("😢 روزهای تنها", callback_data="menu_lonely"),
             InlineKeyboardButton("📖 رمان", callback_data="menu_novel")],
            [InlineKeyboardButton("🏙️ شهری بازی", callback_data="menu_city"),
             InlineKeyboardButton("🔙 منوی اصلی", callback_data="back_main")],
        ]
        await query.edit_message_text(
            "📚 **منوی بیشتر** ✨",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    if data == "back_main":
        await start(update, context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "👋 سلام! خوش اومدی 🌟\n\nیکی از موضوعات رو انتخاب کن:"
    await update.message.reply_text(text, reply_markup=main_menu_keyboard())


async def clean_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = await update.message.reply_text("✅ منوی قدیمی پاک شد.", reply_markup=ReplyKeyboardRemove())
        await asyncio.sleep(3)
        await msg.delete()
    except:
        pass


def main():
    if not TELEGRAM_TOKEN:
        logger.error("توکن پیدا نشد!")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler(["clean", "remove", "clear"], clean_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    logger.info("ربات روشن شد!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
