import os
import random
import logging
import sqlite3
import requests
from datetime import datetime, date
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ========== تنظیمات اولیه ==========
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# ضد اسپم
user_message_timestamps = defaultdict(list)

# ========== دیتابیس ==========
DB_PATH = "group_database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, username TEXT, topic TEXT, memory_text TEXT, sentiment TEXT, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_stats (user_id TEXT PRIMARY KEY, points INTEGER DEFAULT 0, level INTEGER DEFAULT 1, title TEXT DEFAULT "تازه وارد", last_active TEXT, total_memories INTEGER DEFAULT 0, daily_quest_done INTEGER DEFAULT 0, last_daily_quest TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_badges (user_id TEXT, badge_name TEXT, date_earned TEXT, PRIMARY KEY (user_id, badge_name))''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_purchases (user_id TEXT, item_id TEXT, purchase_date TEXT, PRIMARY KEY (user_id, item_id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS music_requests (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, song_name TEXT, date TEXT)''')
    conn.commit()
    conn.close()

init_db()

# ========== لول و تایتل ==========
def calculate_level(points): return points // 100 + 1

def get_title(level):
    titles = {1: "تازه وارد", 2: "عضو فعال", 3: "عضو ویژه", 4: "کاربر طلایی", 5: "کاربر الماسی", 6: "افسانه", 7: "اسطوره"}
    return titles.get(level if level <= 7 else 7, "افسانه‌ای")

def update_user_stats(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT points, total_memories FROM user_stats WHERE user_id=?", (user_id,))
    result = c.fetchone()
    if result:
        points, memories = result
        new_level = calculate_level(points)
        new_title = get_title(new_level)
        c.execute("UPDATE user_stats SET level=?, title=? WHERE user_id=?", (new_level, new_title, user_id))
        conn.commit()
    conn.close()

def add_points(user_id, points, action):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO user_stats (user_id, points, last_active) VALUES (?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET points = points + ?, last_active = ?",
              (user_id, points, datetime.now().isoformat(), points, datetime.now().isoformat()))
    if action == "memory":
        c.execute("UPDATE user_stats SET total_memories = total_memories + 1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    update_user_stats(user_id)
    check_badges(user_id)

# ========== مدال ==========
def check_badges(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT points, total_memories FROM user_stats WHERE user_id=?", (user_id,))
    points, memories = c.fetchone()
    badges = []
    if memories >= 5: badges.append("نویسنده آماتور")
    if memories >= 20: badges.append("نویسنده حرفه‌ای")
    if points >= 500: badges.append("ثروتمند")
    if points >= 1000: badges.append("میلیونر")
    for badge in badges:
        try:
            c.execute("INSERT INTO user_badges (user_id, badge_name, date_earned) VALUES (?,?,?)", (user_id, badge, datetime.now().isoformat()))
        except: pass
    conn.commit()
    conn.close()

def get_badges(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT badge_name FROM user_badges WHERE user_id=?", (user_id,))
    badges = [row[0] for row in c.fetchall()]
    conn.close()
    return badges

# ========== چالش روزانه (اصلاح شده) ==========
DAILY_QUESTS = [
    {"name": "نویسنده", "desc": "✍️ ۱ خاطره جدید بنویس", "reward": 20, "action": "memory"},
    {"name": "جستجوگر", "desc": "🎵 ۱ آهنگ جستجو کن", "reward": 15, "action": "music"},
]

def get_daily_quest(user_id):
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT daily_quest_done, last_daily_quest FROM user_stats WHERE user_id=?", (user_id,))
    result = c.fetchone()
    if not result:
        c.execute("INSERT INTO user_stats (user_id, points, last_active, daily_quest_done, last_daily_quest) VALUES (?, 0, ?, 0, ?)",
                  (user_id, datetime.now().isoformat(), today))
        conn.commit()
        quest = random.choice(DAILY_QUESTS)
        conn.close()
        return {"completed": False, "quest": quest}
    last_date = result[1]
    if last_date == today:
        conn.close()
        return {"completed": result[0] == 1, "quest": None if result[0] == 1 else random.choice(DAILY_QUESTS)}
    else:
        quest = random.choice(DAILY_QUESTS)
        c.execute("UPDATE user_stats SET daily_quest_done=0, last_daily_quest=? WHERE user_id=?", (today, user_id))
        conn.commit()
        conn.close()
        return {"completed": False, "quest": quest}

def complete_quest(user_id):
    today = date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT daily_quest_done FROM user_stats WHERE user_id=?", (user_id,))
    result = c.fetchone()
    if result and result[0] == 0:
        c.execute("UPDATE user_stats SET daily_quest_done=1 WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()
        add_points(user_id, 20, "quest")
        return True
    conn.close()
    return False

# ========== جدول لیگ ==========
def get_leaderboard():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT user_id, points, level, title FROM user_stats ORDER BY points DESC LIMIT 10")
    results = c.fetchall()
    conn.close()
    return results

# ========== فروشگاه ==========
SHOP = {
    "tit1": {"name": "🎭 سلطان خاطره", "price": 200, "type": "title", "value": "سلطان خاطره"},
    "tit2": {"name": "👑 شاهزاده احساسات", "price": 350, "type": "title", "value": "شاهزاده احساسات"},
}

def buy_item(user_id, item_id):
    if item_id not in SHOP:
        return False, "آیتم نامعتبر"
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT points FROM user_stats WHERE user_id=?", (user_id,))
    points = c.fetchone()
    if not points or points[0] < SHOP[item_id]["price"]:
        conn.close()
        return False, "امتیاز کافی نیست"
    try:
        c.execute("INSERT INTO user_purchases (user_id, item_id, purchase_date) VALUES (?,?,?)", (user_id, item_id, datetime.now().isoformat()))
        c.execute("UPDATE user_stats SET points = points - ? WHERE user_id=?", (SHOP[item_id]["price"], user_id))
        if SHOP[item_id]["type"] == "title":
            c.execute("UPDATE user_stats SET title = ? WHERE user_id=?", (SHOP[item_id]["value"], user_id))
        conn.commit()
        conn.close()
        return True, "خرید موفق! ✅"
    except:
        conn.close()
        return False, "قبلاً خریدی"

# ========== ضد اسپم ==========
def check_spam(user_id):
    now = datetime.now()
    user_times = user_message_timestamps[user_id]
    user_times = [t for t in user_times if (now - t).total_seconds() < 10]
    user_times.append(now)
    user_message_timestamps[user_id] = user_times
    return len(user_times) > 5

# ========== فال ==========
FORTUNES = [
    "✨ امروز روز خوبی برات داره! یه اتفاق قشنگ منتظرته 🌟",
    "🌙 امشب بوی عشق میاد... شاید یه پیام خاص بیاد 💌",
    "💫 ستاره‌ها میگن امروز بهترین روز برای شروع چیزای جدید هست",
    "🌸 یه لبخند ساده میتونه دنیات رو عوض کنه، امروز امتحان کن",
]

def get_fortune(): return random.choice(FORTUNES)

# ========== بازی حدس عدد (اصلاح شده کامل) ==========
number_games = {}

async def start_number_game(update, user_id):
    number = random.randint(1, 100)
    number_games[user_id] = {"number": number, "attempts": 0, "max": 5}
    await update.message.reply_text(
        "🎮 *بازی حدس عدد شروع شد!*\n\n"
        "🔢 یه عدد بین *1 تا 100* انتخاب کن\n"
        f"🎯 تو {number_games[user_id]['max']} شانس داری\n\n"
        "✏️ عدد مورد نظرت رو بنویس:",
        parse_mode="Markdown"
    )

def guess_number(user_id, guess):
    if user_id not in number_games:
        return None, None
    game = number_games[user_id]
    game["attempts"] += 1
    
    if guess == game["number"]:
        del number_games[user_id]
        return True, game["attempts"]
    elif game["attempts"] >= game["max"]:
        correct = game["number"]
        del number_games[user_id]
        return False, correct
    elif guess < game["number"]:
        return "بیشتر", game["attempts"]
    else:
        return "کمتر", game["attempts"]

# ========== جستجوی آهنگ ==========
def search_song(song_name):
    try:
        url = f"https://api.deezer.com/search?q={song_name.replace(' ', '%20')}&limit=3"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            return [{"title": track["title"], "artist": track["artist"]["name"], "link": track["link"]} for track in data.get("data", [])[:3]]
    except: pass
    return []

# ========== کیبورد ==========
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("🌙 شب‌های مهتابی"), KeyboardButton("🌿 موضوعات زندگی")],
        [KeyboardButton("🤝 ادب و احترام"), KeyboardButton("❤️ خاطرات عشق")],
        [KeyboardButton("🏙️ شهری بازی"), KeyboardButton("😢 روزهای تنها")],
        [KeyboardButton("🎉 سرگرمی"), KeyboardButton("📖 رمان")],
        [KeyboardButton("🤣 خنده‌دار"), KeyboardButton("🎵 جستجوی آهنگ")],
        [KeyboardButton("📊 آمار من"), KeyboardButton("🏆 جدول لیگ")],
        [KeyboardButton("🎁 فروشگاه"), KeyboardButton("⭐ چالش روزانه")],
        [KeyboardButton("🔮 فال امروز"), KeyboardButton("🎮 بازی حدس عدد")],
        [KeyboardButton("🤖 مدیریت گروه")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ========== محتوای موضوعات ==========
TOPICS_DB = {
    "🌙 شب‌های مهتابی": {"id": "moonlit_nights", "static_texts": ["🌙 شب مهتابی لب دریا...", "🌊 شب‌هایی که ماه روی آب می‌تابه..."], "questions": ["خاطره از شب مهتابی داری؟"]},
    "🌿 موضوعات زندگی": {"id": "life_topics", "static_texts": ["🌿 زندگی یعنی هر روز یه شروع تازه..."], "questions": ["بهترین نصیحت زندگی چیه؟"]},
    "🤝 ادب و احترام": {"id": "respect", "static_texts": ["🤝 ادب نشونه بزرگیه..."], "questions": ["احترام یعنی چی؟"]},
    "❤️ خاطرات عشق": {"id": "love_memories", "static_texts": ["❤️ عشق یعنی وقتی اسمشو میبینی لبخند میزنی..."], "questions": ["قشنگ‌ترین خاطره عشقیت رو بنویس"]},
    "🏙️ شهری بازی": {"id": "city_game", "static_texts": ["🏙️ شهر شبا قشنگه..."], "questions": ["کدوم شهر رو بیشتر دوست داری؟"]},
    "😢 روزهای تنها": {"id": "lonely_days", "static_texts": ["😢 روزهای تنها سخته..."], "questions": ["تو روزای تنهایی چیکار میکنی؟"]},
    "🎉 سرگرمی": {"id": "entertainment", "static_texts": ["🎉 سرگرمی با دوستا..."], "questions": ["بهترین فیلمی که دیدی؟"]},
    "📖 رمان": {"id": "novel", "static_texts": ["📖 رمان خوندن یعنی توی هزار تا زندگی زندگی کردی..."], "questions": ["آخرین کتابی که خوندی؟"]},
    "🤣 خنده‌دار": {"id": "funny", "static_texts": ["🤣 رفتم رژیم بگیرم دکتر عوض کردم..."], "questions": ["بهترین جوکی که بلدی بگو"]},
    "🎵 جستجوی آهنگ": {"id": "music", "static_texts": [], "questions": []},
}

# ========== هندلر استارت ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 سلام {user.first_name}! به ربات هوشمند خوش اومدی 🌟\n\n"
        f"🎁 هر خاطره = ۱۰ امتیاز\n⭐ هر لول = ۱۰۰ امتیاز\n🏆 مدال و دستاورد\n\n"
        f"یه موضوع انتخاب کن 👇",
        reply_markup=get_main_keyboard()
    )

# ========== هندلر اصلی ==========
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or update.effective_user.first_name
    
    if check_spam(user_id):
        await update.message.reply_text("⏳ آرامتر! لطفاً چند ثانیه صبر کن")
        return 0
    
    # بررسی منشن در گروه
    bot_username = context.bot.username
    is_mentioned = False
    is_private = update.message.chat.type == "private"
    
    if update.message.chat.type in ["group", "supergroup"]:
        if update.message.entities:
            for entity in update.message.entities:
                if entity.type == "mention":
                    mentioned = text[entity.offset:entity.offset+entity.length]
                    if mentioned == f"@{bot_username}":
                        is_mentioned = True
                        break
        if text in TOPICS_DB or text in ["📊 آمار من", "🏆 جدول لیگ", "🎁 فروشگاه", "⭐ چالش روزانه", "🔮 فال امروز", "🎮 بازی حدس عدد", "🤖 مدیریت گروه"]:
            is_mentioned = True
        if not is_mentioned:
            return 0
    
    # ========== بازی حدس عدد (اصلاح شده) ==========
    if user_id in number_games:
        try:
            guess = int(text.strip())
            if guess < 1 or guess > 100:
                await update.message.reply_text("❌ عدد باید بین 1 تا 100 باشه!")
                return 0
            
            result, extra = guess_number(user_id, guess)
            
            if result is None:
                return 0
            elif result is True:
                add_points(user_id, 15, "game")
                await update.message.reply_text(f"🎉 آفرین! در {extra} بار حدس زدی! +۱۵ امتیاز", reply_markup=get_main_keyboard())
            elif result is False:
                await update.message.reply_text(f"💀 بازی باخت! عدد {extra} بود\n🍃 دوباره امتحان کن: /game", reply_markup=get_main_keyboard())
            elif result == "بیشتر":
                await update.message.reply_text(f"📈 برو بالاتر! شانس باقی: {5 - extra}")
            elif result == "کمتر":
                await update.message.reply_text(f"📉 بیا پایین‌تر! شانس باقی: {5 - extra}")
            return 0
        except ValueError:
            if text != "🎮 بازی حدس عدد":
                await update.message.reply_text("❌ لطفاً یه عدد بین 1 تا 100 وارد کن!")
                return 0
    
    # جستجوی آهنگ
    if context.user_data.get("waiting_music"):
        context.user_data["waiting_music"] = False
        results = search_song(text)
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO music_requests (user_id, song_name, date) VALUES (?,?,?)", (user_id, text, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        if results:
            keyboard = [[InlineKeyboardButton(f"🎵 {r['title']} - {r['artist']}", url=r['link'])] for r in results]
            await update.message.reply_text(f"🎵 نتایج برای {text}:", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text("❌ آهنگی پیدا نشد")
        return 0
    
    # ثبت خاطره
    if context.user_data.get("waiting_for_memory"):
        topic_id = context.user_data["waiting_for_memory"]
        topic_name = context.user_data.get("current_topic_name", "موضوع")
        add_points(user_id, 10, "memory")
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO memories (user_id, username, topic, memory_text, date) VALUES (?,?,?,?,?)", (user_id, username, topic_id, text, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"✅ خاطره ثبت شد! +۱۰ امتیاز", reply_markup=get_main_keyboard())
        context.user_data["waiting_for_memory"] = None
        return 0
    
    # آمار من
    if text == "📊 آمار من":
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT points, level, title, total_memories FROM user_stats WHERE user_id=?", (user_id,))
        result = c.fetchone()
        conn.close()
        badges = get_badges(user_id)
        stats = result if result else (0, 1, "تازه وارد", 0)
        await update.message.reply_text(
            f"📊 *آمار شما*\n\n⭐ امتیاز: {stats[0]}\n🏆 لول: {stats[1]}\n🎭 تایتل: {stats[2]}\n📝 خاطرات: {stats[3]}\n🎖️ مدال‌ها: {', '.join(badges) if badges else 'نداری'}",
            parse_mode="Markdown", reply_markup=get_main_keyboard()
        )
        return 0
    
    # جدول لیگ
    if text == "🏆 جدول لیگ":
        leaderboard = get_leaderboard()
        msg = "🏆 *جدول برترین‌ها*\n\n"
        for i, (uid, pts, lvl, title) in enumerate(leaderboard[:10], 1):
            msg += f"{i}. {title[:10]} | لول {lvl} | {pts} امتیاز\n"
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_main_keyboard())
        return 0
    
    # فروشگاه
    if text == "🎁 فروشگاه":
        msg = "🛒 *فروشگاه*\n\n"
        for id, item in SHOP.items():
            msg += f"• {item['name']} - {item['price']} امتیاز\n"
        msg += "\nبرای خرید: /buy کدآیتم\nمثال: /buy tit1"
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_main_keyboard())
        return 0
    
    # چالش روزانه
    if text == "⭐ چالش روزانه":
        quest = get_daily_quest(user_id)
        if quest["completed"]:
            await update.message.reply_text("✅ امروز چالش روزانه رو انجام دادی!", reply_markup=get_main_keyboard())
        else:
            await update.message.reply_text(
                f"⭐ *چالش امروز:* {quest['quest']['desc']}\n🏆 جایزه: {quest['quest']['reward']} امتیاز\n\n"
                f"✅ برای تایید انجام چالش بنویس:\n`/complete_quest`",
                parse_mode="Markdown", reply_markup=get_main_keyboard()
            )
        return 0
    
    # فال امروز
    if text == "🔮 فال امروز":
        add_points(user_id, 5, "fortune")
        await update.message.reply_text(f"🔮 فال امروز تو:\n\n{get_fortune()}\n\n✨ +۵ امتیاز", reply_markup=get_main_keyboard())
        return 0
    
    # بازی حدس عدد
    if text == "🎮 بازی حدس عدد":
        if user_id in number_games:
            await update.message.reply_text("🎮 یه بازی در حال اجراست! عدد بفرست:")
        else:
            await start_number_game(update, user_id)
        return 0
    
    # مدیریت گروه
    if text == "🤖 مدیریت گروه":
        await update.message.reply_text(f"🤖 *مدیریت گروه*\n\nبرای صحبت: منشن کن @{bot_username}\nیا از دکمه‌ها استفاده کن", parse_mode="Markdown", reply_markup=get_main_keyboard())
        return 0
    
    # جستجوی آهنگ
    if text == "🎵 جستجوی آهنگ":
        context.user_data["waiting_music"] = True
        await update.message.reply_text("🎵 اسم آهنگ رو بنویس:", reply_markup=get_main_keyboard())
        return 0
    
    # موضوعات
    if text in TOPICS_DB:
        topic_data = TOPICS_DB[text]
        content = random.choice(topic_data["static_texts"]) if topic_data["static_texts"] else f"✨ {text} ✨"
        if topic_data["questions"]:
            content += f"\n\n💬 {random.choice(topic_data['questions'])}\n\n📝 جوابتو بنویس (+۱۰ امتیاز)"
            context.user_data["waiting_for_memory"] = topic_data["id"]
            context.user_data["current_topic_name"] = text
        await update.message.reply_text(content, reply_markup=get_main_keyboard())
        return 0
    
    # پیام آزاد در پیوی
    if not is_private:
        return 0
    await update.message.reply_text("❌ از دکمه‌های پایین استفاده کن", reply_markup=get_main_keyboard())
    return 0

# ========== دستورات ==========
async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ /buy کدآیتم\nمثال: /buy tit1")
        return
    success, msg = buy_item(str(update.effective_user.id), context.args[0])
    await update.message.reply_text(msg)

async def complete_quest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if complete_quest(user_id):
        await update.message.reply_text("✅ چالش تکمیل شد! +۲۰ امتیاز 🌟", reply_markup=get_main_keyboard())
    else:
        await update.message.reply_text("❌ چالش امروز رو قبلاً انجام دادی یا فعال نیست", reply_markup=get_main_keyboard())

async def game_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id in number_games:
        await update.message.reply_text("🎮 یه بازی در حال اجراست! عدد بفرست:")
    else:
        await start_number_game(update, user_id)

# ========== اجرا ==========
def main():
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN تنظیم نشده!")
        return
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy_command))
    app.add_handler(CommandHandler("complete_quest", complete_quest_command))
    app.add_handler(CommandHandler("game", game_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("ربات با ۱۰ سیستم پیشرفته شروع به کار کرد!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
