import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# ==================== متون طنز و خنده‌دار ====================
JOKES = [
    "😂 یه روز به یه خیار گفتم چرا همیشه سردی؟\nگفت: آخه من توی یخچال بزرگ شدم! 🥒❄️",
    "😂 رفتم دکتر گفتم: دلم درد می‌کنه\nدکتر گفت: از چی می‌خوری؟\nگفتم: از بس که می‌خندم! 🤣",
    "😂 به یه تخم‌مرغ گفتم: چرا اینقدر شکننده‌ای؟\nگفت: من که تخم‌مرغم، نه آجر! 🥚",
    "😂 یه روز به ماهی گفتم: چرا همیشه سکوت می‌کنی؟\nگفت: آخه توی آبم، حرف زدن بلد نیستم! 🐟",
    "😂 گفتم: چرا گربه اینقدر مغروره؟\nگفت: من که گربم، نه سگ که دنبالت بدوم! 🐱",
    "😂 رفتم خونه‌ی دوستم، دیدم دیوارا رنگ و رو رفته\nگفتم: چرا رنگ نمی‌زنی؟\nگفت: آخه دیوارا هم حق سکوت دارن! 🧱",
    "😂 به موز گفتم: چرا همیشه خمیده‌ای؟\nگفت: من که موزم، نه نیزه! 🍌",
    "😂 یه روز به پیاز گفتم: چرا گریه ام می‌گیری؟\nگفت: من که پیازم، نه گل سرخ! 🧅",
    "😂 رفتم نانوایی گفتم: این نان چقدر؟\nگفت: ۵۰۰ تومن\nگفتم: این که پوچه!\nگفت: نه، نانه! 🥖",
    "😂 به خودکار گفتم: چقدر می‌نویسی؟\nگفت: تا وقتی جوهر داشته باشم! ✒️",
    "😂 یه روز به ساعت گفتم: چرا همیشه می‌دوی؟\nگفت: من که ساعتم، نه لاک‌پشت! ⏰",
    "😂 رفتم دکتر، گفت: چاقی!\nگفتم: نه، خوش‌گل و خوش‌گل! 🍔",
    "😂 به بادکنک گفتم: چرا اینقدر بادی؟\nگفت: آخه خالی که نیستم! 🎈",
    "😂 یه روز به آینه گفتم: چرا همیشه تکرار می‌کنی؟\nگفت: من که آینه‌ام، نه طوطی! 🪞",
    "😂 رفتم کبابی گفتم: این کباب چقدر؟\nگفت: گرونه!\nگفتم: مهم نیست، پول دارم!\nگفت: نه بابا، کباب گوشته! 🥩",
    "🤣 مشتری: این میوه چقدر؟\nفروشنده: ۲ کیلو ۱۰ تومن\nمشتری: چرا گرون؟\nفروشنده: گرون نیست، خربزه‌است! 🍈",
    "😂 به کتاب گفتم: چقدر می‌دونی؟\nگفت: هرچی توش نوشتن! 📚",
    "😂 یه روز به تلفن گفتم: چرا اینقدر حرف می‌زنی؟\nگفت: من که تلفنم، نه مجسمه! 📱",
    "😂 رفتم مغازه گفتم: این پیراهن چقدر؟\nگفت: ۱۰۰ تومن\nگفتم: چرا اینقدر؟\nگفت: آخه ابریشمه!\nگفتم: نه بابا، نخیسه! 👕",
    "😂 به ماه گفتم: چرا همیشه گردی؟\nگفت: من که ماهم، نه توپ فوتبال! 🌙",
    "🤣 یه روز به سیر گفتم: چرا بوی تندی داری؟\nگفت: من که سیرم، نه عطر فرانسوی! 🧄",
    "😂 رفتم آزمایشگاه گفتم: این لام چقدر؟\nگفت: ۲۰۰ تومن\nگفتم: چرا شیشه‌ایه؟\nگفت: نه بابا، روشناییه! 💡",
    "😂 به گوجه گفتم: چرا اینقدر قرمزی؟\nگفت: خجالت می‌کشم از این سوالات! 🍅",
    "😂 یه روز به قوری گفتم: چرا همیشه بخار می‌کنی؟\nگفت: آخه داغونم! ☕",
    "😂 رفتم عطاری گفتم: این گیاه چقدر؟\nگفت: ۵۰ تومن\nگفتم: چرا خشکه؟\nگفت: نه بابا، آویشنه! 🌿",
    "🤣 به مداد گفتم: چرا همیشه می‌شکنی؟\nگفت: آخه ذوق دارم بنویسم! ✏️",
    "😂 به درخت گفتم: چرا همه رو می‌پوشونی؟\nگفت: من که درختم، نه چتر! 🌳",
    "😂 رفتم قصابی گفتم: این گوشت چقدر؟\nگفت: گوسفندیه!\nگفتم: نه بابا، گرون نیست! 🐑",
    "😂 به شمع گفتم: چرا گریه می‌کنی؟\nگفت: آخه آب میشم! 🕯️",
    "😂 یه روز به یخ گفتم: چرا اینقدر سردی؟\nگفت: من که یخم، نه آتش! 🧊",
    "🤣 رفتم میوه‌فروشی گفتم: این هندونه چقدر؟\nگفت: ۱۰ تومن کیلویی\nگفتم: چرا درشته؟\nگفت: نه بابا، شیرینه! 🍉",
    "😂 به دریا گفتم: چقدر آب داری؟\nگفت: بی‌نهایت!\nگفتم: چرا شوری؟\nگفت: آخه نمک گیرم! 🌊"
]

NIGHT_TEXTS = [
    "🌙 شب مهتابی، لب دریا، صدای امواج...\nکاش کنارم بودی تا این لحظه رو باهم حس کنیم 💫",
    "🌊 شب‌هایی که ماه روی آب می‌تابه\nو دلم برای یه نفر تنگ میشه که هنوز نیومده... 🤍",
    "🌙 لب دریا نشستم، باد موهامو به هم ریخت\nفکر کردم به تو، به این شب، به این سکوت قشنگ... ✨",
]

LIFE_TEXTS = [
    "🌿 زندگی یعنی هر روز یه شروع تازه\nنفس بکش، لبخند بزن، ادامه بده 💚",
    "☀️ مهربونی کن، حتی وقتی کسی نمیبینه\nدنیا به مهربون‌ها نیاز داره 🤍",
]

RESPECT_TEXTS = [
    "🤝 ادب نشونه بزرگیه، نه ضعف\nبا احترام حرف بزن، با احترام گوش بده 🌟",
    "👑 بزرگ‌ترین قدرت آدم اینه که\nبدون توهین حرفشو بزنه 💎",
]

LOVE_TEXTS = [
    "❤️ عشق یعنی وقتی اسمشو میبینی\nبی‌اختیار لبخند میزنی 🌹",
    "💕 خاطره‌های خوب\nهیچ وقت پاک نمیشن، فقط محو میشن 🌸",
]

LONELY_TEXTS = [
    "😢 روزهای تنها سخته\nولی یادت باشه، فردا همیشه بهتره 🌙",
]

NOVEL_TEXTS = [
    "📖 رمان خوندن یعنی\nتوی هزار تا زندگی زندگی کردی 🌟",
]

CITY_TEXTS = [
    "🏙️ شهر شبا قشنگه\nوقتی چراغا روشنن و خیابونا خلوت 🌃",
]

FUN_TEXTS = [
    "🎉 سرگرمی یعنی بیخیال همه چیز بشی\nو فقط لذت ببری 🎊",
]

def get_random_text(category: str) -> str:
    texts_map = {
        "night": NIGHT_TEXTS, "life": LIFE_TEXTS, "respect": RESPECT_TEXTS,
        "love": LOVE_TEXTS, "lonely": LONELY_TEXTS, "novel": NOVEL_TEXTS,
        "city": CITY_TEXTS, "fun": FUN_TEXTS, "joke": JOKES
    }
    texts = texts_map.get(category, JOKES)
    return random.choice(texts)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور استارت - نمایش منوی اصلی"""
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
    text = "👋 سلام! خوش اومدی 🌟\n\nیه موضوع انتخاب کن:"
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str, title: str):
    """نمایش متن تصادفی از یک دسته"""
    query = update.callback_query
    await query.answer()
    
    text = get_random_text(category)
    keyboard = [
        [InlineKeyboardButton("🔄 متن بعدی", callback_data=f"menu_{category}"),
         InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")],
    ]
    
    await query.edit_message_text(
        f"**{title}**\n\n{text}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def random_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش یک متن کاملاً تصادفی"""
    query = update.callback_query
    await query.answer()
    
    all_cats = ["night", "life", "respect", "love", "lonely", "novel", "city", "fun", "joke"]
    cat = random.choice(all_cats)
    names = {
        "night": "🌙 شب", "life": "🌿 زندگی", "respect": "🤝 ادب", 
        "love": "❤️ عشق", "lonely": "😢 تنها", "novel": "📖 رمان", 
        "city": "🏙️ شهر", "fun": "🎉 سرگرمی", "joke": "😂 جوک"
    }
    text = get_random_text(cat)
    keyboard = [
        [InlineKeyboardButton("🎲 یکی دیگه", callback_data="menu_random"),
         InlineKeyboardButton("🏠 منوی اصلی", callback_data="back_main")]
    ]
    
    await query.edit_message_text(
        f"**🎲 {names[cat]}:**\n\n{text}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def second_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی دوم (بیشتر)"""
    query = update.callback_query
    await query.answer()
    
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

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """هندلر اصلی دکمه‌ها"""
    data = update.callback_query.data
    
    if data == "back_main":
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
        text = "👋 سلام! خوش اومدی 🌟\n\nیه موضوع انتخاب کن:"
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    elif data == "menu_second":
        await second_menu(update, context)
    
    elif data == "menu_random":
        await random_text(update, context)
    
    elif data == "menu_night":
        await show_category(update, context, "night", "🌙 شب‌های مهتابی")
    
    elif data == "menu_life":
        await show_category(update, context, "life", "🌿 موضوعات زندگی")
    
    elif data == "menu_respect":
        await show_category(update, context, "respect", "🤝 ادب و احترام")
    
    elif data == "menu_love":
        await show_category(update, context, "love", "❤️ خاطرات عشق")
    
    elif data == "menu_lonely":
        await show_category(update, context, "lonely", "😢 روزهای تنها")
    
    elif data == "menu_fun":
        await show_category(update, context, "fun", "🎉 سرگرمی")
    
    elif data == "menu_novel":
        await show_category(update, context, "novel", "📖 رمان")
    
    elif data == "menu_city":
        await show_category(update, context, "city", "🏙️ شهری بازی")
    
    elif data == "menu_joke":
        await show_category(update, context, "joke", "😂 خنده و شوخی")

def main():
    """راه‌اندازی ربات"""
    if not TELEGRAM_TOKEN:
        logger.error("❌ توکن تلگرام پیدا نشد!")
        print("❌ توکن تلگرام پیدا نشد! متغیر محیطی TELEGRAM_TOKEN رو تنظیم کن.")
        return
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # اضافه کردن هندلرها بدون ConversationHandler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    logger.info("✅ ربات با موفقیت راه‌اندازی شد!")
    print("✅ ربات روشن شد و در گروه‌ها هم کار میکنه!")
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
