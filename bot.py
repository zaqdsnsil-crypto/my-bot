import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

MAIN_MENU = 0


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌙 شب‌های مهتابی", callback_data="menu_night"),
         InlineKeyboardButton("🌿 موضوعات زندگی", callback_data="menu_life")],
        [InlineKeyboardButton("🤝 ادب و احترام", callback_data="menu_respect"),
         InlineKeyboardButton("❤️ خاطرات عشق", callback_data="menu_love")],
        [InlineKeyboardButton("🏙️ شهری بازی", callback_data="menu_city"),
         InlineKeyboardButton("😢 روزهای تنها", callback_data="menu_lonely")],
        [InlineKeyboardButton("🎉 سرگرمی", callback_data="menu_fun"),
         InlineKeyboardButton("📖 رمان", callback_data="menu_novel")],
        [InlineKeyboardButton("🤖 مدیریت گروه", callback_data="menu_admin")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "👋 سلام! خوش اومدی 🌟\n\nیه موضوع انتخاب کن:"

    # حذف کیبورد قدیمی (ReplyKeyboard) اگه وجود داشت
    if update.message:
        await update.message.reply_text(
            text,
            reply_markup=reply_markup
        )
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    return MAIN_MENU


async def night_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texts = [
        "🌙 شب مهتابی، لب دریا، صدای امواج...\nکاش کنارم بودی تا این لحظه رو باهم حس کنیم 💫",
        "🌊 شب‌هایی که ماه روی آب می‌تابه\nو دلم برای یه نفر تنگ میشه که هنوز نیومده... 🤍",
        "🌙 لب دریا نشستم، باد موهامو به هم ریخت\nفکر کردم به تو، به این شب، به این سکوت قشنگ... ✨",
        "💫 شب مهتابیه و دریا آروم\nفقط دلم یه دست گرم می‌خواد توی این سرما 🌊",
        "🌕 ماه تموم بود و دریا آینه\nمن فقط نشسته بودم و به تو فکر می‌کردم 🤍",
        "🌙 بوی دریا، صدای موج، نور ماه...\nهمه چیز هست جز تو، که کاش بودی 💙",
        "⭐ شب‌های مهتابی لب دریا\nیه جور آرامشی داره که هیچ جای دیگه‌ای نیست 🌊",
    ]
    keyboard = [
        [InlineKeyboardButton("🔄 متن بعدی", callback_data="menu_night")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]
    ]
    await query.edit_message_text(
        random.choice(texts),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU


async def life_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texts = [
        "🌿 زندگی یعنی هر روز یه شروع تازه\nنفس بکش، لبخند بزن، ادامه بده 💚",
        "☀️ مهربونی کن، حتی وقتی کسی نمیبینه\nدنیا به مهربون‌ها نیاز داره 🤍",
        "🌱 دوست داشتن یاد گرفتنیه\nاول خودتو دوست داشته باش، بقیه‌اش میاد 💛",
        "🦋 هر سختی که رد میشه\nقوی‌تر از قبل میشی، باور کن 💪",
        "🌸 زندگی خوب یعنی\nکمتر قضاوت، بیشتر محبت، همیشه امید ✨",
        "🌻 هر روز یه فرصته\nبرای اینکه آدم بهتری باشی 🌟",
        "💚 خوشبختی توی لحظه‌های کوچیکه\nیه لبخند، یه آغوش، یه قهوه داغ... 🍵",
        "🌈 بعد از هر بارون\nیه رنگین‌کمون منتظرته، صبور باش 🌦️",
        "💎 قدر آدم‌های خوب زندگیتو بدون\nاونا نادرن، نگه‌شون دار 🤍",
    ]
    keyboard = [
        [InlineKeyboardButton("🔄 متن بعدی", callback_data="menu_life")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]
    ]
    await query.edit_message_text(
        random.choice(texts),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU


async def respect_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texts = [
        "🤝 ادب نشونه بزرگیه، نه ضعف\nبا احترام حرف بزن، با احترام گوش بده 🌟",
        "👑 بزرگ‌ترین قدرت آدم اینه که\nبدون توهین حرفشو بزنه 💎",
        "🌹 احترام یه چیز دو طرفه‌ست\nبدی، پس دریافت می‌کنی 🤍",
        "✨ با همه با ادب رفتار کن\nچون شخصیت تو رو نشون میده، نه اونا رو 🌿",
        "🕊️ سکوت در برابر بی‌احترامی\nبعضی وقت‌ها باهوشانه‌ترین جوابه 💫",
        "🌺 آدم با ادب\nهمه جا محبوبه، همه جا موفقه 🏆",
        "💙 احترام گذاشتن به دیگران\nیعنی به خودت احترام میذاری 🤝",
        "🌟 بزرگ باش، حتی وقتی\nکوچیک‌ها اذیتت می‌کنن 👑",
    ]
    keyboard = [
        [InlineKeyboardButton("🔄 متن بعدی", callback_data="menu_respect")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]
    ]
    await query.edit_message_text(
        random.choice(texts),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU


async def love_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texts = [
        "❤️ عشق یعنی وقتی اسمشو میبینی\nبی‌اختیار لبخند میزنی 🌹",
        "💕 خاطره‌های خوب\nهیچ وقت پاک نمیشن، فقط محو میشن 🌸",
        "🌹 دوستت دارم\nسه کلمه‌ای که دنیا رو عوض میکنه 💫",
        "💖 عاشقی یعنی\nبدترین روزاتم با بودن اون خوب بشه ☀️",
        "🌸 قلبم یه جایی گیره\nپیش کسی که شاید خبر نداره 💙",
    ]
    keyboard = [
        [InlineKeyboardButton("🔄 متن بعدی", callback_data="menu_love")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]
    ]
    await query.edit_message_text(
        random.choice(texts),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU


async def lonely_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texts = [
        "😢 روزهای تنها سخته\nولی یادت باشه، فردا همیشه بهتره 🌙",
        "🌧️ بعضی شبا دلت میگیره\nبدون دلیل، بدون توضیح... فقط دلگیری 💙",
        "😔 تنهایی یعنی\nوسط جمع باشی و دلت بخواد بری 🍂",
        "🌙 شبا که همه خوابن\nفکرا بیدار میشن و دلتنگی شروع میشه 💫",
        "🤍 تو تنها نیستی\nیه جایی یه نفر دقیقاً همین حسو داره 🌟",
    ]
    keyboard = [
        [InlineKeyboardButton("🔄 متن بعدی", callback_data="menu_lonely")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]
    ]
    await query.edit_message_text(
        random.choice(texts),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU


async def fun_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texts = [
        "🎉 سرگرمی وقتیه که\nبا دوستات بخندی تا اشک بیاد 😂",
        "😂 بهترین درمان دنیا\nیه خنده از ته دل 🎊",
        "🎭 زندگی کوتاهه\nبیشتر بخند، کمتر جدی باش 🎈",
        "🎉 امروز رو جشن بگیر\nچون فردا یه روز دیگه‌ست 🥳",
        "😄 شادی مسریه\nیه لبخند بزن، ببین چی میشه 🌟",
    ]
    keyboard = [
        [InlineKeyboardButton("🔄 متن بعدی", callback_data="menu_fun")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]
    ]
    await query.edit_message_text(
        random.choice(texts),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU


async def novel_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texts = [
        "📖 رمان خوندن یعنی\nتوی هزار تا زندگی زندگی کردی 🌟",
        "📚 کتاب بهترین دوست آدمه\nهیچ وقت قضاوتت نمیکنه 💙",
        "🌹 یه رمان خوب\nمثل یه سفره که از خونه تکون نمیخوری ✨",
        "📖 وقتی کتاب تموم میشه\nیه جور غمی داری که خوشحالم هست 💫",
        "📚 دنیای کتاب‌ها\nبی‌نهایته، هیچ وقت تنها نمیشی 🌸",
    ]
    keyboard = [
        [InlineKeyboardButton("🔄 متن بعدی", callback_data="menu_novel")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]
    ]
    await query.edit_message_text(
        random.choice(texts),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU


async def city_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    texts = [
        "🏙️ شهر شبا قشنگه\nوقتی چراغا روشنن و خیابونا خلوت 🌃",
        "🌆 شهر پر از آدمه\nولی همه دنبال یه چیزن که ندارن 🏙️",
        "🌉 پل‌های شهر\nچقدر داستان دیدن، چقدر قدم دیدن 💫",
        "🏙️ کافه‌های شهر\nبوی قهوه، صدای موزیک، آدم‌های غریبه 🍵",
        "🌃 شب‌های شهر\nیه جور زندگیه که روزا نداره ✨",
    ]
    keyboard = [
        [InlineKeyboardButton("🔄 متن بعدی", callback_data="menu_city")],
        [InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]
    ]
    await query.edit_message_text(
        random.choice(texts),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU


async def admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]]
    await query.edit_message_text(
        "🤖 مدیریت گروه\n\nبرای فعال کردن، منو به گروه اضافه کن و /start بزن.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "back_main":
        return await start(update, context)
    elif data == "menu_night":
        return await night_menu(update, context)
    elif data == "menu_life":
        return await life_menu(update, context)
    elif data == "menu_respect":
        return await respect_menu(update, context)
    elif data == "menu_love":
        return await love_menu(update, context)
    elif data == "menu_lonely":
        return await lonely_menu(update, context)
    elif data == "menu_fun":
        return await fun_menu(update, context)
    elif data == "menu_novel":
        return await novel_menu(update, context)
    elif data == "menu_city":
        return await city_menu(update, context)
    elif data == "menu_admin":
        return await admin_menu(update, context)


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        # فیلتر PRIVATE حذف شد - الان تو گروه هم کار میکنه
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [CallbackQueryHandler(button_handler)],
        },
        fallbacks=[CommandHandler("start", start)],
        # برای گروه‌ها این گزینه لازمه
        per_chat=True,
    )
    app.add_handler(conv_handler)
    logger.info("ربات شروع به کار کرد!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
