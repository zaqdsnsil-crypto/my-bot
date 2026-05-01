import os
import random
import logging
import json
import sqlite3
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ========== تنظیمات اولیه ==========
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# ========== دیتابیس اصلی ==========
DB_PATH = "group_database.db"

def init_db():
    """راه‌اندازی دیتابیس با تمام جداول"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # جدول خاطرات کاربران
    c.execute('''CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        username TEXT,
        topic TEXT,
        memory_text TEXT,
        sentiment TEXT,
        date TEXT
    )''')
    
    # جدول امتیازات کاربران
    c.execute('''CREATE TABLE IF NOT EXISTS user_points (
        user_id TEXT PRIMARY KEY,
        points INTEGER DEFAULT 0,
        last_active TEXT
    )''')
    
    # جدول درخواست‌های آهنگ
    c.execute('''CREATE TABLE IF NOT EXISTS music_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        song_name TEXT,
        date TEXT
    )''')
    
    conn.commit()
    conn.close()

init_db()

# ========== سیستم هوشمند احساسات (Sentiment Analysis ساده) ==========
def analyze_sentiment(text):
    """تحلیل احساسات ساده برای تشخیص شادی، غم، عشق"""
    happy_words = ["خوشحال", "عشق", "دوست دارم", "بهترین", "شاد", "لبخند", "خنده", "جشن", "هیجان"]
    sad_words = ["غمگین", "تنها", "دلم گرفته", "گریه", "درد", "ناراحت", "اشک", "دلتنگی"]
    love_words = ["عشق", "دوستت دارم", "قلب", "دلم برات تنگ", "کنارتم", "عاشق"]
    
    text_lower = text.lower()
    if any(word in text_lower for word in love_words):
        return "عاشقانه"
    elif any(word in text_lower for word in happy_words):
        return "شاد"
    elif any(word in text_lower for word in sad_words):
        return "غمگین"
    return "خنثی"

# ========== ذخیره خاطره در دیتابیس ==========
def save_memory(user_id, username, topic, memory_text):
    sentiment = analyze_sentiment(memory_text)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO memories (user_id, username, topic, memory_text, sentiment, date) VALUES (?,?,?,?,?,?)",
              (user_id, username, topic, memory_text, sentiment, datetime.now().isoformat()))
    
    # اضافه کردن امتیاز برای ثبت خاطره
    c.execute("INSERT INTO user_points (user_id, points, last_active) VALUES (?, 10, ?) ON CONFLICT(user_id) DO UPDATE SET points = points + 10, last_active = ?",
              (user_id, datetime.now().isoformat(), datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    return sentiment

# ========== دریافت خاطرات تصادفی از دیتابیس ==========
def get_random_memory(topic):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT memory_text, username, sentiment FROM memories WHERE topic=? ORDER BY RANDOM() LIMIT 1", (topic,))
    result = c.fetchone()
    conn.close()
    if result:
        return f"📖 {result[0]}\n\n👤 {result[1]}\n💭 حس: {result[2]}"
    return None

# ========== دریافت آمار کاربر ==========
def get_user_stats(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT points FROM user_points WHERE user_id=?", (user_id,))
    points = c.fetchone()
    c.execute("SELECT COUNT(*) FROM memories WHERE user_id=?", (user_id,))
    memories_count = c.fetchone()
    conn.close()
    return {
        "points": points[0] if points else 0,
        "memories": memories_count[0] if memories_count else 0
    }

# ========== جستجوی حرفه‌ای آهنگ (چند API) ==========
def search_song_advanced(song_name):
    """جستجوی آهنگ با Deezer API + لینک یوتیوب"""
    results = []
    
    # 1. Deezer API
    try:
        deezer_url = f"https://api.deezer.com/search?q={song_name.replace(' ', '%20')}&limit=3"
        resp = requests.get(deezer_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for track in data.get("data", [])[:2]:
                results.append({
                    "title": track["title"],
                    "artist": track["artist"]["name"],
                    "link": track["link"],
                    "duration": track["duration"],
                    "source": "Deezer"
                })
    except:
        pass
    
    # 2. لینک یوتیوب
    youtube_query = song_name.replace(" ", "+")
    youtube_link = f"https://www.youtube.com/results?search_query={youtube_query}"
    
    # 3. لینک اسپاتیفای
    spotify_link = f"https://open.spotify.com/search/{youtube_query}"
    
    return results, youtube_link, spotify_link

# ========== محتوای هوشمند هر موضوع (با دیتابیس) ==========
TOPICS_DB = {
    "🌙 شب‌های مهتابی": {
        "id": "moonlit_nights",
        "static_texts": [
            "🌙 شب مهتابی، لب دریا، صدای امواج...\nکاش کنارم بودی تا این لحظه رو باهم حس کنیم 💫",
            "🌊 شب‌هایی که ماه روی آب می‌تابه\nو دلم برای یه نفر تنگ میشه که هنوز نیومده... 🤍",
            "💫 شب مهتابیه و دریا آروم\nفقط دلم یه دست گرم می‌خواد توی این سرما 🌊",
            "🌕 ماه تموم بود و دریا آینه\nمن فقط نشسته بودم و به تو فکر می‌کردم 🤍"
        ],
        "questions": [
            "🌙 برات خاطره‌ای از شب‌های مهتابی داری؟ برام بنویس 🤍",
            "⭐ کنار چه کسی دوست داری یه شب مهتابی باشی؟"
        ]
    },
    "🌿 موضوعات زندگی": {
        "id": "life_topics",
        "static_texts": [
            "🌿 زندگی یعنی هر روز یه شروع تازه\nنفس بکش، لبخند بزن، ادامه بده 💚",
            "🌸 زندگی خوب یعنی\nکمتر قضاوت، بیشتر محبت، همیشه امید ✨",
            "🌈 بعد از هر بارون\nیه رنگین‌کمون منتظرته، صبور باش 🌦️",
            "💎 قدر آدم‌های خوب زندگیتو بدون\nاونا نادرن، نگه‌شون دار 🤍"
        ],
        "questions": [
            "🌿 بهترین نصیحتی که تا حالا شنیدی چیه؟",
            "💚 چه چیزی توی زندگی باعث آرامشت میشه؟"
        ]
    },
    "🤝 ادب و احترام": {
        "id": "respect",
        "static_texts": [
            "🤝 ادب نشونه بزرگیه، نه ضعف\nبا احترام حرف بزن، با احترام گوش بده 🌟",
            "👑 بزرگ‌ترین قدرت آدم اینه که\nبدون توهین حرفشو بزنه 💎",
            "💙 احترام گذاشتن به دیگران\nیعنی به خودت احترام میذاری 🤝"
        ],
        "questions": [
            "🤝 به نظرت احترام چه شکلی توی جامعه دیده میشه؟",
            "🌟 چه کسی توی زندگیت بهت یاد داد با احترام باشی؟"
        ]
    },
    "❤️ خاطرات عشق": {
        "id": "love_memories",
        "static_texts": [
            "❤️ عشق یعنی وقتی اسمشو میبینی\nبی‌اختیار لبخند میزنی 🌹",
            "💕 خاطره‌های خوب\nهیچ وقت پاک نمیشن، فقط محو میشن 🌸",
            "💖 عاشقی یعنی\nبدترین روزاتم با بودن اون خوب بشه ☀️"
        ],
        "questions": [
            "❤️ قشنگ‌ترین خاطره عشقی که داری رو برام بنویس 🤍",
            "🌸 اون شخص خاص توی زندگیت چطور توی قلبت جا گرفت؟"
        ]
    },
    "🏙️ شهری بازی": {
        "id": "city_game",
        "static_texts": [
            "🏙️ شهر شبا قشنگه\nوقتی چراغا روشنن و خیابونا خلوت 🌃",
            "🌆 شهر پر از آدمه\nولی همه دنبال یه چیزن که ندارن 🏙️"
        ],
        "questions": [
            "🏙️ کدوم شهر رو بیشتر دوست داری؟ چرا؟",
            "🌃 خاطره‌ات از یه شب به‌یادماندنی توی شهر چیه؟"
        ]
    },
    "😢 روزهای تنها": {
        "id": "lonely_days",
        "static_texts": [
            "😢 روزهای تنها سخته\nولی یادت باشه، فردا همیشه بهتره 🌙",
            "🤍 تو تنها نیستی\nیه جایی یه نفر دقیقاً همین حسو داره 🌟"
        ],
        "questions": [
            "😢 چه چیزی توی روزهای تنهایی بهت آرامش میده؟",
            "💙 یه حرف دوس داری به کسی بزنی که نمی‌تونی؟ اینجا برام بنویس"
        ]
    },
    "🎉 سرگرمی": {
        "id": "entertainment",
        "static_texts": [
            "🎉 سرگرمی وقتیه که\nبا دوستات بخندی تا اشک بیاد 😂",
            "🎭 زندگی کوتاهه\nبیشتر بخند، کمتر جدی باش 🎈"
        ],
        "questions": [
            "🎉 بهترین بازی یا فیلمی که اخیراً دیدی چیه؟",
            "😂 یه اتفاق خنده‌دار که برات افتاده رو بگو"
        ]
    },
    "📖 رمان": {
        "id": "novel",
        "static_texts": [
            "📖 رمان خوندن یعنی\nتوی هزار تا زندگی زندگی کردی 🌟",
            "📚 کتاب بهترین دوست آدمه\nهیچ وقت قضاوتت نمیکنه 💙"
        ],
        "questions": [
            "📖 آخرین کتابی که خوندی چی بود؟ چقدر دوستش داشتی؟",
            "🌹 اگه یه رمان بنویسی، اسمش چی میذاری؟"
        ]
    },
    "🤣 خنده‌دار": {
        "id": "funny",
        "static_texts": [
            "🤣 رفتم رژیم بگیرم\nدکتر گفت کمتر بخور، منم دکترو عوض کردم 😂",
            "😂 گفتم دیگه شکلات نمیخورم\nبعد گفتم یکی دیگه\nبعد گفتم آخریه\nالان پاکت خالیه 🍫💀"
        ],
        "questions": [
            "😂 بهترین جوکی که بلدی رو بگو!",
            "🤣 یه اتفاق خنده‌دار که هیچوقت فراموش نمیکنی رو برام بنویس"
        ]
    },
    "🎵 جستجوی آهنگ": {
        "id": "music",
        "static_texts": [],
        "questions": []
    }
}

# ========== کیبورد اصلی ==========
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("🌙 شب‌های مهتابی"), KeyboardButton("🌿 موضوعات زندگی")],
        [KeyboardButton("🤝 ادب و احترام"), KeyboardButton("❤️ خاطرات عشق")],
        [KeyboardButton("🏙️ شهری بازی"), KeyboardButton("😢 روزهای تنها")],
        [KeyboardButton("🎉 سرگرمی"), KeyboardButton("📖 رمان")],
        [KeyboardButton("🤣 خنده‌دار"), KeyboardButton("🎵 جستجوی آهنگ")],
        [KeyboardButton("📊 آمار من"), KeyboardButton("🤖 مدیریت گروه")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ========== هندلر استارت ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 سلام {user.first_name}! خوش اومدی 🌟\n\n"
        f"📝 این یه گروه هوشمنده\n"
        f"🎁 هر خاطره = ۱۰ امتیاز\n"
        f"💎 با امتیازا میتونی بعداً جوایز بگیری\n\n"
        f"یه موضوع انتخاب کن:",
        reply_markup=get_main_keyboard()
    )
    return 0

# ========== هندلر اصلی پیام‌ها ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or update.effective_user.first_name
    
    # حالت انتظار برای جستجوی آهنگ
    if context.user_data.get("waiting_music"):
        context.user_data["waiting_music"] = False
        results, youtube_link, spotify_link = search_song_advanced(text)
        
        # ذخیره درخواست آهنگ
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO music_requests (user_id, song_name, date) VALUES (?,?,?)",
                  (user_id, text, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        if results:
            keyboard_buttons = []
            for track in results:
                keyboard_buttons.append([InlineKeyboardButton(
                    f"🎵 {track['title']} - {track['artist']} ({track['source']})",
                    url=track['link']
                )])
            keyboard_buttons.append([InlineKeyboardButton("▶️ جستجو در یوتیوب", url=youtube_link)])
            keyboard_buttons.append([InlineKeyboardButton("🎧 جستجو در اسپاتیفای", url=spotify_link)])
            keyboard = InlineKeyboardMarkup(keyboard_buttons)
            
            await update.message.reply_text(
                f"🎵 نتایج جستجو برای: *{text}*\n\n{len(results)} نتیجه پیدا شد 👇",
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        else:
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("▶️ جستجو در یوتیوب", url=youtube_link)],
                [InlineKeyboardButton("🎧 جستجو در اسپاتیفای", url=spotify_link)]
            ])
            await update.message.reply_text(
                f"🎵 آهنگی برای '{text}' تو سرویس‌ها پیدا نشد!\n\nولی می‌تونی اینجا بگردی 👇",
                reply_markup=keyboard
            )
        return 0
    
    # آمار کاربر
    if text == "📊 آمار من":
        stats = get_user_stats(user_id)
        await update.message.reply_text(
            f"📊 *آمار شما*\n\n"
            f"⭐ امتیاز: {stats['points']}\n"
            f"📝 تعداد خاطرات ثبت‌شده: {stats['memories']}\n"
            f"🎁 هر خاطره = ۱۰ امتیاز\n\n"
            f"💡 بیشتر خاطره بنویس تا امتیاز بیشتری بگیری!",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return 0
    
    # مدیریت گروه
    if text == "🤖 مدیریت گروه":
        await update.message.reply_text(
            "🤖 *مدیریت گروه*\n\n"
            "✅ منو به گروه اضافه کن\n"
            "✅ دستور /start رو بزن\n"
            "✅ از کیبورد پایین موضوعات رو انتخاب کن\n\n"
            "🔧 *امکانات:*\n"
            "• ذخیره خاطرات کاربران\n"
            "• جستجوی حرفه‌ای آهنگ\n"
            "• سیستم امتیازدهی\n"
            "• تحلیل احساسات خاطرات",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        return 0
    
    # جستجوی آهنگ (فعال کردن حالت انتظار)
    if text == "🎵 جستجوی آهنگ":
        context.user_data["waiting_music"] = True
        await update.message.reply_text(
            "🎵 اسم آهنگ یا خواننده رو بنویس 👇\n\n"
            "🎤 مثال: Shajarian, Eden, Baraye...",
            reply_markup=get_main_keyboard()
        )
        return 0
    
    # بررسی موضوعات (ابتدا خاطره ثبت می‌شه، بعد پاسخ داده میشه)
    if text in TOPICS_DB:
        topic_data = TOPICS_DB[text]
        topic_id = topic_data["id"]
        
        # ثبت خاطره اگه کاربر متنی اضافه کرده باشه (بررسی state جداگانه)
        if context.user_data.get(f"writing_for_{topic_id}"):
            # این بخش تو هندلر دوم پردازش میشه که برات مینویسم
            pass
        
        # انتخاب تصادفی از محتوای ثابت
        static_texts = topic_data["static_texts"]
        if static_texts:
            content = random.choice(static_texts)
        else:
            content = f"✨ {text} ✨\n\nحالت چطوره؟ هر چی دوست داری برام بنویس 📝"
        
        # چک کردن خاطرات ذخیره شده از بقیه
        random_memory = get_random_memory(topic_id)
        if random_memory:
            content += f"\n\n━━━━━━━━━━━━━━━\n📖 *خاطره یکی از کاربرا:*\n{random_memory}"
        
        # اضافه کردن سوال برای تعامل
        if "questions" in topic_data and topic_data["questions"]:
            question = random.choice(topic_data["questions"])
            content += f"\n\n💬 *سوال لحظه:*\n{question}\n\n📝 می‌تونی جوابتو برام بنویسی (خاطره ثبت میشه و +۱۰ امتیاز)"
        
        # ذخیره تو context که کاربر در حال پاسخ به کدوم موضوع هست
        context.user_data["current_topic"] = topic_id
        context.user_data["current_topic_name"] = text
        
        await update.message.reply_text(content, parse_mode="Markdown", reply_markup=get_main_keyboard())
        
        # اگر سوال پرسیده شد، منتظر جواب میمونیم (برای ثبت خاطره)
        if "questions" in topic_data and topic_data["questions"]:
            context.user_data["waiting_for_memory"] = topic_id
    
    else:
        # اگر کاربر در حال پاسخ به سوال یک موضوع هست
        if context.user_data.get("waiting_for_memory"):
            topic_id = context.user_data["waiting_for_memory"]
            topic_name = context.user_data.get("current_topic_name", "موضوع")
            
            # ذخیره خاطره کاربر
            sentiment = save_memory(user_id, username, topic_id, text)
            
            # ارسال پیام تایید با امتیاز
            await update.message.reply_text(
                f"✅ خاطره‌ات توی {topic_name} ثبت شد! ❤️\n"
                f"📊 احساس: {sentiment}\n"
                f"⭐ +۱۰ امتیاز گرفتی!\n\n"
                f"🍃 بازم از منو انتخاب کن 🌟",
                reply_markup=get_main_keyboard()
            )
            
            # پاک کردن حالت انتظار
            context.user_data["waiting_for_memory"] = None
            context.user_data["current_topic"] = None
        else:
            await update.message.reply_text(
                "❓ این گزینه رو ندارم 😅\n\n"
                "لطفاً از دکمه‌های پایین صفحه یه موضوع انتخاب کن 👇",
                reply_markup=get_main_keyboard()
            )
    
    return 0

# ========== اجرای اصلی ==========
def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN تنظیم نشده!")
        return
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("ربات پیشرفته با سیستم هوشمند شروع به کار کرد!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
