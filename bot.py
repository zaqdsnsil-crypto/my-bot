import os
import random
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
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


def get_main_keyboard():
    keyboard = [
        [KeyboardButton("🌙 شب‌های مهتابی"), KeyboardButton("🌿 موضوعات زندگی")],
        [KeyboardButton("🤝 ادب و احترام"), KeyboardButton("❤️ خاطرات عشق")],
        [KeyboardButton("🏙️ شهری بازی"), KeyboardButton("😢 روزهای تنها")],
        [KeyboardButton("🎉 سرگرمی"), KeyboardButton("📖 رمان")],
        [KeyboardButton("🤣 خنده‌دار"), KeyboardButton("🎵 جستجوی آهنگ")],
        [KeyboardButton("🤖 مدیریت گروه")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 سلام! خوش اومدی 🌟\n\nیه موضوع انتخاب کن:",
        reply_markup=get_main_keyboard()
    )
    return MAIN_MENU


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # حالت جستجو موزیک
    if context.user_data.get("waiting_music"):
        context.user_data["waiting_music"] = False
        encoded = text.replace(" ", "+")
        youtube_url = f"https://www.youtube.com/results?search_query={encoded}"
        spotify_url = f"https://open.spotify.com/search/{encoded}"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("▶️ جستجو در یوتیوب", url=youtube_url)],
            [InlineKeyboardButton("🎧 جستجو در اسپاتیفای", url=spotify_url)],
        ])
        await update.message.reply_text(
            f"🎵 نتایج جستجو برای: *{text}*\n\nروی یکی بزن 👇",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        return MAIN_MENU

    if text == "🌙 شب‌های مهتابی":
        texts = [
            "🌙 شب مهتابی، لب دریا، صدای امواج...\nکاش کنارم بودی تا این لحظه رو باهم حس کنیم 💫",
            "🌊 شب‌هایی که ماه روی آب می‌تابه\nو دلم برای یه نفر تنگ میشه که هنوز نیومده... 🤍",
            "🌙 لب دریا نشستم، باد موهامو به هم ریخت\nفکر کردم به تو، به این شب، به این سکوت قشنگ... ✨",
            "💫 شب مهتابیه و دریا آروم\nفقط دلم یه دست گرم می‌خواد توی این سرما 🌊",
            "🌕 ماه تموم بود و دریا آینه\nمن فقط نشسته بودم و به تو فکر می‌کردم 🤍",
            "🌙 بوی دریا، صدای موج، نور ماه...\nهمه چیز هست جز تو، که کاش بودی 💙",
            "⭐ شب‌های مهتابی لب دریا\nیه جور آرامشی داره که هیچ جای دیگه‌ای نیست 🌊",
        ]
        await update.message.reply_text(random.choice(texts), reply_markup=get_main_keyboard())

    elif text == "🌿 موضوعات زندگی":
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
        await update.message.reply_text(random.choice(texts), reply_markup=get_main_keyboard())

    elif text == "🤝 ادب و احترام":
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
        await update.message.reply_text(random.choice(texts), reply_markup=get_main_keyboard())

    elif text == "❤️ خاطرات عشق":
        texts = [
            "❤️ عشق یعنی وقتی اسمشو میبینی\nبی‌اختیار لبخند میزنی 🌹",
            "💕 خاطره‌های خوب\nهیچ وقت پاک نمیشن، فقط محو میشن 🌸",
            "🌹 دوستت دارم\nسه کلمه‌ای که دنیا رو عوض میکنه 💫",
            "💖 عاشقی یعنی\nبدترین روزاتم با بودن اون خوب بشه ☀️",
            "🌸 قلبم یه جایی گیره\nپیش کسی که شاید خبر نداره 💙",
        ]
        await update.message.reply_text(random.choice(texts), reply_markup=get_main_keyboard())

    elif text == "🏙️ شهری بازی":
        texts = [
            "🏙️ شهر شبا قشنگه\nوقتی چراغا روشنن و خیابونا خلوت 🌃",
            "🌆 شهر پر از آدمه\nولی همه دنبال یه چیزن که ندارن 🏙️",
            "🌉 پل‌های شهر\nچقدر داستان دیدن، چقدر قدم دیدن 💫",
            "🏙️ کافه‌های شهر\nبوی قهوه، صدای موزیک، آدم‌های غریبه 🍵",
            "🌃 شب‌های شهر\nیه جور زندگیه که روزا نداره ✨",
        ]
        await update.message.reply_text(random.choice(texts), reply_markup=get_main_keyboard())

    elif text == "😢 روزهای تنها":
        texts = [
            "😢 روزهای تنها سخته\nولی یادت باشه، فردا همیشه بهتره 🌙",
            "🌧️ بعضی شبا دلت میگیره\nبدون دلیل، بدون توضیح... فقط دلگیری 💙",
            "😔 تنهایی یعنی\nوسط جمع باشی و دلت بخواد بری 🍂",
            "🌙 شبا که همه خوابن\nفکرا بیدار میشن و دلتنگی شروع میشه 💫",
            "🤍 تو تنها نیستی\nیه جایی یه نفر دقیقاً همین حسو داره 🌟",
        ]
        await update.message.reply_text(random.choice(texts), reply_markup=get_main_keyboard())

    elif text == "🎉 سرگرمی":
        texts = [
            "🎉 سرگرمی وقتیه که\nبا دوستات بخندی تا اشک بیاد 😂",
            "😂 بهترین درمان دنیا\nیه خنده از ته دل 🎊",
            "🎭 زندگی کوتاهه\nبیشتر بخند، کمتر جدی باش 🎈",
            "🎉 امروز رو جشن بگیر\nچون فردا یه روز دیگه‌ست 🥳",
            "😄 شادی مسریه\nیه لبخند بزن، ببین چی میشه 🌟",
        ]
        await update.message.reply_text(random.choice(texts), reply_markup=get_main_keyboard())

    elif text == "📖 رمان":
        texts = [
            "📖 رمان خوندن یعنی\nتوی هزار تا زندگی زندگی کردی 🌟",
            "📚 کتاب بهترین دوست آدمه\nهیچ وقت قضاوتت نمیکنه 💙",
            "🌹 یه رمان خوب\nمثل یه سفره که از خونه تکون نمیخوری ✨",
            "📖 وقتی کتاب تموم میشه\nیه جور غمی داری که خوشحالم هست 💫",
            "📚 دنیای کتاب‌ها\nبی‌نهایته، هیچ وقت تنها نمیشی 🌸",
        ]
        await update.message.reply_text(random.choice(texts), reply_markup=get_main_keyboard())

    elif text == "🤣 خنده‌دار":
        texts = [
            "🤣 رفتم رژیم بگیرم\nدکتر گفت کمتر بخور، منم دکترو عوض کردم 😂",
            "💀 ساعت ۲ شب گشنمه\nولی صدای یخچال از اتاقم میاد و ترسیدم 🌙😂",
            "😭 گفتم امروز زود بیدار میشم\nساعت زنگ زد، قبولش نکردم، رد شد 😴",
            "🤡 رفیقم گفت: «تو خیلی باهوشی»\nفهمیدم یه چیزی میخواد 😂💀",
            "🧠 مغزم شبا: بیا فکر کنیم به همه چیز\nمن: الان؟!\nمغزم: آره، الان بهترین وقته 🌙",
            "😂 گفتم دیگه شکلات نمیخورم\nبعد گفتم یکی دیگه\nبعد گفتم آخریه\nالان پاکت خالیه 🍫💀",
            "🤣 رفتم آشپزخونه آب بخورم\nنشستم، غذا خوردم، فیلم دیدم\nآب یادم رفت 😭",
            "😅 وقتی بهم میگن «چرا دیر اومدی؟»\nجواب میدم: «ترافیک»\nتو خونه بودم 🏠😂",
            "💀 من موقع امتحان:\n«همه چیزو بلدم»\nتو جلسه امتحان:\nاسمم یادم نیست 😭📝",
            "🤡 خریدم که صرفه‌جویی کنم\nتخفیف ۵۰٪ دیدم، دو تا خریدم\nالان دو برابر خرج کردم 😂💸",
            "😂 دوستم زنگ زد گفت:\n«کجایی؟»\nگفتم: «خونه»\nگفت: «منم»\nگفتم: «پس چرا زنگ زدی؟» 📞🤦",
            "🌙 ساعت ۳ شبه، باید بخوابم\nمغز: بیا یه سوال فلسفی حل کنیم\nمن: باشه 💀",
            "😭 گفتم امسال کتاب بخونم\nاینستاگرام: این ری‌الز خوبه\nمن: باشه فقط یکی 📱💀",
            "🤣 وقتی میگم «الان میام»\nیعنی ۲۰ دقیقه دیگه\nوقتی میگم «نزدیکم»\nیعنی هنوز خونه‌ام 😅",
            "🍕 پیتزا سفارش دادم\nگفت ۳۰ دقیقه\nمن ۲۹ دقیقه دم در وایسادم 😂🚪",
        ]
        await update.message.reply_text(random.choice(texts), reply_markup=get_main_keyboard())

    elif text == "🎵 جستجوی آهنگ":
        context.user_data["waiting_music"] = True
        await update.message.reply_text(
            "🎵 اسم آهنگ یا خواننده رو بنویس 👇",
            reply_markup=get_main_keyboard()
        )

    elif text == "🤖 مدیریت گروه":
        await update.message.reply_text(
            "🤖 مدیریت گروه\n\nبرای فعال کردن، منو به گروه اضافه کن و /start بزن.",
            reply_markup=get_main_keyboard()
        )

    else:
        await update.message.reply_text(
            "یه گزینه از منو انتخاب کن 👇",
            reply_markup=get_main_keyboard()
        )

    return MAIN_MENU


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("ربات شروع به کار کرد!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
