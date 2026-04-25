import os
import random
import datetime
from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)

TOKEN = os.environ.get("TOKEN")
GROUP_LINK = "https://t.me/sgjujbc"
CHAT_ID = int(os.environ.get("CHAT_ID", "-1001003887975782"))

warnings = {}
trivia_answers = {}
number_games = {}

BAD_WORDS = ["فحش1", "فحش2", "بد1"]

JOKES = [
    "یه نفر رفت دکتر گفت دکتر همه بهم میگن دیوونه!\nدکتر گفت: خب برو بیرون نوبت بعدی! 😂",
    "معلم: چرا دیر اومدی؟\nشاگرد: مدرسه ساعت 8 شروع میشه، منم ساعت 8 رفتم خونه! 😂",
    "یه نفر زنگ زد پیتزافروشی: یه پیتزا بدید!\nگفتن آدرس؟\nگفت روی جعبه بنویسید تبریک تولد! 😂",
    "دوستم گفت داری چیکار میکنی؟\nگفتم هیچی!\nگفت کِی تموم میشه؟ 😂",
    "بابام گفت برو اتاقتو مرتب کن!\nرفتم در اتاقمو قفل کردم! 😂",
]

FACTS = [
    "مغز انسان حدود 86 میلیارد نورون داره!",
    "اختاپوس سه قلب داره و خونش آبیه!",
    "زمین در هر ثانیه 30 کیلومتر دور خورشید میچرخه!",
    "کوسه ها از دایناسورها قدیمی ترن!",
    "عسل هرگز فاسد نمیشه، عسل 3000 ساله پیدا شده!",
]

TOP_SONGS = [
    "Blinding Lights - The Weeknd",
    "Shape of You - Ed Sheeran",
    "Despacito - Luis Fonsi",
    "Uptown Funk - Bruno Mars",
    "Rolling in the Deep - Adele",
]

TRIVIA = [
    {"q": "پایتخت فرانسه کجاست؟", "a": "پاریس", "opts": ["لندن", "پاریس", "برلین", "رم"]},
    {"q": "بزرگترین سیاره منظومه شمسی کدومه؟", "a": "مشتری", "opts": ["زحل", "اورانوس", "مشتری", "نپتون"]},
    {"q": "چند ساعت در یک شبانه روز وجود داره؟", "a": "24", "opts": ["12", "24", "36", "48"]},
    {"q": "سریع ترین حیوان روی زمین کدومه؟", "a": "یوزپلنگ", "opts": ["شیر", "اسب", "یوزپلنگ", "ببر"]},
]

async def is_admin(update: Update) -> bool:
    user = update.message.from_user
    chat = update.message.chat
    member = await chat.get_member(user.id)
    return member.status in ["administrator", "creator"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! من ربات قدرتمند گروهم!\n\n"
        "دستورات مدیریت:\n"
        "/ban - بن کردن\n"
        "/unban - آنبن کردن\n"
        "/mute - میوت کردن\n"
        "/unmute - آنمیوت کردن\n"
        "/kick - کیک کردن\n"
        "/pin - پین کردن\n"
        "/warn - اخطار دادن\n"
        "/userinfo - اطلاعات کاربر\n"
        "/stats - آمار گروه\n\n"
        "بازی و سرگرمی:\n"
        "/joke - جوک\n"
        "/fact - حقیقت جالب\n"
        "/music - آهنگ برتر\n"
        "/trivia - سوال تریویا\n"
        "/guess - بازی حدس عدد\n"
        "/dice - تاس\n"
        "/rps - سنگ کاغذ قیچی\n"
        "/magic - پیش بینی\n"
        "/roast - متلک\n"
        "/love - سنجش عشق\n\n"
        f"گروه ما: {GROUP_LINK}"
    )

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"سلام {member.full_name} عزیز!\n"
            f"خوش اومدی به گروه ما!\n"
            f"گروه ما: {GROUP_LINK}"
        )

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("فقط ادمین میتونه!")
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.ban_chat_member(update.message.chat_id, user.id)
        await update.message.reply_text(f"{user.full_name} بن شد!")
    else:
        await update.message.reply_text("روی پیام کاربر ریپلای بزن!")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("فقط ادمین میتونه!")
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.unban_chat_member(update.message.chat_id, user.id)
        await update.message.reply_text(f"{user.full_name} آنبن شد!")
    else:
        await update.message.reply_text("روی پیام کاربر ریپلای بزن!")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("فقط ادمین میتونه!")
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        until = datetime.datetime.now() + datetime.timedelta(hours=1)
        await context.bot.restrict_chat_member(
            update.message.chat_id, user.id,
            ChatPermissions(can_send_messages=False), until_date=until
        )
        await update.message.reply_text(f"{user.full_name} یک ساعت میوت شد!")
    else:
        await update.message.reply_text("روی پیام کاربر ریپلای بزن!")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("فقط ادمین میتونه!")
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.restrict_chat_member(
            update.message.chat_id, user.id,
            ChatPermissions(can_send_messages=True, can_send_photos=True, can_send_videos=True)
        )
        await update.message.reply_text(f"{user.full_name} آنمیوت شد!")
    else:
        await update.message.reply_text("روی پیام کاربر ریپلای بزن!")

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("فقط ادمین میتونه!")
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.ban_chat_member(update.message.chat_id, user.id)
        await context.bot.unban_chat_member(update.message.chat_id, user.id)
        await update.message.reply_text(f"{user.full_name} کیک شد!")
    else:
        await update.message.reply_text("روی پیام کاربر ریپلای بزن!")

async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("فقط ادمین میتونه!")
        return
    if update.message.reply_to_message:
        await context.bot.pin_chat_message(update.message.chat_id, update.message.reply_to_message.message_id)
        await update.message.reply_text("پیام پین شد!")
    else:
        await update.message.reply_text("روی پیام ریپلای بزن!")

async def userinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.reply_to_message.from_user if update.message.reply_to_message else update.message.from_user
    await update.message.reply_text(
        f"اطلاعات کاربر:\n\nنام: {user.full_name}\nآیدی: {user.id}\nیوزرنیم: @{user.username if user.username else 'ندارد'}"
    )

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("فقط ادمین میتونه!")
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        uid = user.id
        warnings[uid] = warnings.get(uid, 0) + 1
        if warnings[uid] >= 3:
            await context.bot.ban_chat_member(update.message.chat_id, uid)
            await update.message.reply_text(f"{user.full_name} 3 اخطار گرفت و بن شد!")
            warnings[uid] = 0
        else:
            await update.message.reply_text(f"{user.full_name} اخطار {warnings[uid]}/3 گرفت!")
    else:
        await update.message.reply_text("روی پیام کاربر ریپلای بزن!")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.message.chat
    count = await context.bot.get_chat_member_count(chat.id)
    await update.message.reply_text(f"آمار گروه:\n\nتعداد اعضا: {count}\nنام گروه: {chat.title}")

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"جوک روز:\n\n{random.choice(JOKES)}")

async def fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"حقیقت جالب:\n\n{random.choice(FACTS)}")

async def music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    songs = random.sample(TOP_SONGS, 3)
    text = "آهنگ های برتر:\n\n"
    for i, s in enumerate(songs, 1):
        text += f"{i}. {s}\n"
    await update.message.reply_text(text)

async def trivia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = random.choice(TRIVIA)
    opts = q["opts"].copy()
    random.shuffle(opts)
    trivia_answers[update.message.chat_id] = q["a"]
    keyboard = [[InlineKeyboardButton(opt, callback_data=f"trivia_{opt}")] for opt in opts]
    await update.message.reply_text(f"سوال:\n\n{q['q']}", reply_markup=InlineKeyboardMarkup(keyboard))

async def trivia_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data.replace("trivia_", "")
    correct = trivia_answers.get(query.message.chat_id)
    if data == correct:
        await query.edit_message_text(f"آفرین! جواب درسته: {correct}")
    else:
        await query.edit_message_text(f"اشتباه! جواب درست: {correct} بود!")

async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    number = random.randint(1, 100)
    number_games[chat_id] = {"number": number, "tries": 0}
    await update.message.reply_text("بازی حدس عدد!\nعدد 1 تا 100\nبا /try [عدد] حدس بزن!")

async def try_guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id not in number_games:
        await update.message.reply_text("اول /guess بزن!")
        return
    if not context.args:
        await update.message.reply_text("مثال: /try 50")
        return
    try:
        guess_num = int(context.args[0])
    except:
        await update.message.reply_text("عدد صحیح وارد کن!")
        return
    game = number_games[chat_id]
    game["tries"] += 1
    number = game["number"]
    if guess_num == number:
        await update.message.reply_text(f"آفرین! عدد {number} بود! در {game['tries']} بار!")
        del number_games[chat_id]
    elif guess_num < number:
        await update.message.reply_text(f"بزرگتره! تلاش {game['tries']}")
    else:
        await update.message.reply_text(f"کوچکتره! تلاش {game['tries']}")

async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"تاس: {random.randint(1, 6)}")

async def rps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("سنگ", callback_data="rps_rock"),
        InlineKeyboardButton("کاغذ", callback_data="rps_paper"),
        InlineKeyboardButton("قیچی", callback_data="rps_scissors"),
    ]]
    await update.message.reply_text("انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))

async def rps_callback(update, context):
    query = update.callback_query
    await query.answer()
    choice = query.data.replace("rps_", "")
    bot_choice = random.choice(["rock", "paper", "scissors"])
    names = {"rock": "سنگ", "paper": "کاغذ", "scissors": "قیچی"}
    wins = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
    if choice == bot_choice:
        result = "مساوی!"
    elif wins[choice] == bot_choice:
        result = "تو بردی!"
    else:
        result = "من بردم!"
    await query.edit_message_text(f"تو: {names[choice]}\nمن: {names[bot_choice]}\n\n{result}")

async def magic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    preds = ["آینده ات پر از موفقیته!", "یه خبر خوب در راهه!", "امروز روز خوبیه!", "پول بادآورده در راهه!"]
    await update.message.reply_text(f"پیش بینی:\n\n{random.choice(preds)}")

async def roast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    roasts = ["IQ تو به اندازه دمای یخچاله!", "وقتی ساکت میشی همه فکر میکنن باهوش شدی!", "اگه باهوش بودن جرم بود آزاد بودی!"]
    if update.message.reply_to_message:
        name = update.message.reply_to_message.from_user.first_name
        await update.message.reply_text(f"{name}، {random.choice(roasts)}")
    else:
        await update.message.reply_text(random.choice(roasts))

async def love(update: Update, context: ContextTypes.DEFAULT_TYPE):
    percent = random.randint(0, 100)
    bar = "❤" * (percent // 10) + "🖤" * (10 - percent // 10)
    await update.message.reply_text(f"سنجش عشق:\n\n{bar}\n{percent}%")

async def filter_bad_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    for word in BAD_WORDS:
        if word in update.message.text.lower():
            await update.message.delete()
            await context.bot.send_message(update.message.chat_id, f"{update.message.from_user.full_name} پیامت حذف شد!")
            return

async def anti_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    member = await update.message.chat.get_member(update.message.from_user.id)
    if member.status in ["administrator", "creator"]:
        return
    if "t.me/" in update.message.text or "http" in update.message.text:
        await update.message.delete()
        await context.bot.send_message(update.message.chat_id, f"{update.message.from_user.full_name} لینک ارسال نکن!")

async def send_promo(context: ContextTypes.DEFAULT_TYPE):
    msgs = [
        f"گروه ما رو به دوستات معرفی کن!\nلینک: {GROUP_LINK}",
        f"بیا تو گروه ما!\nلینک: {GROUP_LINK}",
    ]
    await context.bot.send_message(chat_id=CHAT_ID, text=random.choice(msgs))

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("unban", unban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("pin", pin))
    app.add_handler(CommandHandler("userinfo", userinfo))
    app.add_handler(CommandHandler("warn", warn))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("fact", fact))
    app.add_handler(CommandHandler("music", music))
    app.add_handler(CommandHandler("trivia", trivia))
    app.add_handler(CommandHandler("guess", guess))
    app.add_handler(CommandHandler("try", try_guess))
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("rps", rps))
    app.add_handler(CommandHandler("magic", magic))
    app.add_handler(CommandHandler("roast", roast))
    app.add_handler(CommandHandler("love", love))
    app.add_handler(CallbackQueryHandler(trivia_callback, pattern="^trivia_"))
    app.add_handler(CallbackQueryHandler(rps_callback, pattern="^rps_"))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filter_bad_words))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_link))
    app.job_queue.run_repeating(send_promo, interval=10800, first=10)
    print("ربات روشنه!")
    app.run_polling()

if __name__ == "__main__":
    main()
