import os
TOKEN = os.environ.get("TOKEN") 

from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import datetime
import random

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 سلام! من ربات مدیریت گروهم!\n\n"
        "🛡 مدیریت:\n"
        "🚫 /ban\n✅ /unban\n🔇 /mute\n🔊 /unmute\n👢 /kick\n📌 /pin\n👤 /userinfo\n\n"
        "🎮 بازی:\n"
        "🎲 /dice\n🪨 /rps\n🔢 /guess\n❓ /trivia\n\n"
        "🎵 سرگرمی:\n"
        "😂 /joke\n💪 /challenge\n🔮 /magic\n🎨 /color\n⭐ /horoscope"
    )

async def is_admin(update: Update) -> bool:
    member = await update.message.chat.get_member(update.message.from_user.id)
    return member.status in ["administrator", "creator"]

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"👋 سلام {member.full_name} عزیز! خوش اومدی 🌟")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("❌ فقط ادمین می‌تونه!")
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.ban_chat_member(update.message.chat_id, user.id)
        await update.message.reply_text(f"🚫 {user.full_name} بن شد!")
    else:
        await update.message.reply_text("↩️ روی پیام کاربر ریپلای بزن!")

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("❌ فقط ادمین می‌تونه!")
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.unban_chat_member(update.message.chat_id, user.id)
        await update.message.reply_text(f"✅ {user.full_name} آنبن شد!")
    else:
        await update.message.reply_text("↩️ روی پیام کاربر ریپلای بزن!")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("❌ فقط ادمین می‌تونه!")
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        until = datetime.datetime.now() + datetime.timedelta(hours=1)
        await context.bot.restrict_chat_member(
            update.message.chat_id, user.id,
            ChatPermissions(can_send_messages=False), until_date=until)
        await update.message.reply_text(f"🔇 {user.full_name} میوت شد!")
    else:
        await update.message.reply_text("↩️ روی پیام کاربر ریپلای بزن!")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("❌ فقط ادمین می‌تونه!")
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.restrict_chat_member(
            update.message.chat_id, user.id,
            ChatPermissions(can_send_messages=True, can_send_photos=True, can_send_videos=True))
        await update.message.reply_text(f"🔊 {user.full_name} آنمیوت شد!")
    else:
        await update.message.reply_text("↩️ روی پیام کاربر ریپلای بزن!")

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("❌ فقط ادمین می‌تونه!")
        return
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        await context.bot.ban_chat_member(update.message.chat_id, user.id)
        await context.bot.unban_chat_member(update.message.chat_id, user.id)
        await update.message.reply_text(f"👢 {user.full_name} کیک شد!")
    else:
        await update.message.reply_text("↩️ روی پیام کاربر ریپلای بزن!")

async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update):
        await update.message.reply_text("❌ فقط ادمین می‌تونه!")
        return
    if update.message.reply_to_message:
        await context.bot.pin_chat_message(update.message.chat_id, update.message.reply_to_message.message_id)
        await update.message.reply_text("📌 پیام پین شد!")
    else:
        await update.message.reply_text("↩️ روی پیام ریپلای بزن!")

async def userinfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.reply_to_message.from_user if update.message.reply_to_message else update.message.from_user
    await update.message.reply_text(
        f"👤 اطلاعات کاربر:\n📛 نام: {user.full_name}\n🆔 آیدی: {user.id}\n👤 یوزرنیم: @{user.username if user.username else 'ندارد'}")

async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🎲 تاس انداختی: {random.randint(1, 6)}")

async def rps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("🪨 سنگ", callback_data="rps_rock"),
        InlineKeyboardButton("📄 کاغذ", callback_data="rps_paper"),
        InlineKeyboardButton("✂️ قیچی", callback_data="rps_scissors"),
    ]]
    await update.message.reply_text("یکی رو انتخاب کن:", reply_markup=InlineKeyboardMarkup(keyboard))

async def rps_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choices = {"rps_rock": "🪨 سنگ", "rps_paper": "📄 کاغذ", "rps_scissors": "✂️ قیچی"}
    wins = {"rps_rock": "rps_scissors", "rps_paper": "rps_rock", "rps_scissors": "rps_paper"}
    user_choice = query.data
    bot_choice = random.choice(list(choices.keys()))
    if user_choice == bot_choice:
        result = "مساوی 🤝"
    elif wins[user_choice] == bot_choice:
        result = "تو بردی 🏆"
    else:
        result = "ربات برد 🤖"
    await query.edit_message_text(f"تو: {choices[user_choice]}\nربات: {choices[bot_choice]}\n\n{result}")

async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["guess_number"] = random.randint(1, 10)
    await update.message.reply_text("🔢 عدد بین ۱ تا ۱۰ حدس بزن! بنویس /answer عدد")

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "guess_number" not in context.user_data:
        await update.message.reply_text("اول /guess بزن!")
        return
    try:
        user_guess = int(context.args[0])
        correct = context.user_data["guess_number"]
        if user_guess == correct:
            await update.message.reply_text("🎉 آفرین درسته!")
            del context.user_data["guess_number"]
        elif user_guess < correct:
            await update.message.reply_text("⬆️ بیشتر!")
        else:
            await update.message.reply_text("⬇️ کمتر!")
    except:
        await update.message.reply_text("مثلاً: /answer 5")

async def trivia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = [
        ("🌍 پایتخت فرانسه؟", "پاریس"),
        ("🌊 بزرگترین اقیانوس؟", "آرام"),
        ("☀️ نزدیکترین ستاره به زمین؟", "خورشید"),
        ("🐋 بزرگترین حیوان جهان؟", "نهنگ آبی"),
    ]
    q, a = random.choice(questions)
    context.user_data["trivia_answer"] = a
    await update.message.reply_text(f"{q}\n\nجواب: /trivia_answer جواب")

async def trivia_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "trivia_answer" not in context.user_data:
        await update.message.reply_text("اول /trivia بزن!")
        return
    if context.args:
        correct = context.user_data["trivia_answer"]
        if " ".join(context.args) in correct:
            await update.message.reply_text("✅ درسته! 🎉")
        else:
            await update.message.reply_text(f"❌ اشتباه! جواب: {correct}")
        del context.user_data["trivia_answer"]

async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes = [
        "😂 چرا دریا شور شد؟ چون ماهی‌ها آنقدر خندیدن که اشکشون درومد!",
        "😄 استاد: چرا دیر اومدی؟\nشاگرد: زود بیدار شدم دیدم هنوز خیلی مونده خوابیدم!",
        "😆 مادر: چرا نمره‌ات افتاده؟\nبچه: معلم سوالایی می‌ده که جوابشو بلده!",
    ]
    await update.message.reply_text(random.choice(jokes))

async def challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    challenges = [
        "💪 ۲۰ تا شنا برو!", "🧘 ۵ دقیقه مدیتیشن کن!",
        "📚 ۱۰ صفحه کتاب بخون!", "💧 یه لیوان آب بخور!",
        "😊 به ۳ نفر پیام بده!", "🎵 یه آهنگ شاد گوش بده!",
    ]
    await update.message.reply_text(random.choice(challenges))

async def magic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    predictions = [
        "🔮 امروز یه خبر خوب می‌شنوی!", "⭐ هفته آینده برات خوبه!",
        "🍀 شانست بالاست!", "💫 یه فرصت طلایی در راهه!",
    ]
    await update.message.reply_text(random.choice(predictions))

async def color(update: Update, context: ContextTypes.DEFAULT_TYPE):
    colors = ["🔴 قرمز", "🟠 نارنجی", "🟡 زرد", "🟢 سبز", "🔵 آبی", "🟣 بنفش"]
    await update.message.reply_text(f"🎨 رنگ تو: {random.choice(colors)}")

async def horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    signs = ["♈ فروردین", "♉ اردیبهشت", "♊ خرداد", "♋ تیر", "♌ مرداد", "♍ شهریور",
             "♎ مهر", "♏ آبان", "♐ آذر", "♑ دی", "♒ بهمن", "♓ اسفند"]
    fortunes = ["روز پرانرژی!", "مراقب مخارجت باش!", "عشق در راهه!", "موفقیت نزدیکه!"]
    await update.message.reply_text(f"{random.choice(signs)}\n\n🔮 {random.choice(fortunes)}")

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
    app.add_handler(CommandHandler("dice", dice))
    app.add_handler(CommandHandler("rps", rps))
    app.add_handler(CommandHandler("guess", guess))
    app.add_handler(CommandHandler("answer", answer))
    app.add_handler(CommandHandler("trivia", trivia))
    app.add_handler(CommandHandler("trivia_answer", trivia_answer))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("challenge", challenge))
    app.add_handler(CommandHandler("magic", magic))
    app.add_handler(CommandHandler("color", color))
    app.add_handler(CommandHandler("horoscope", horoscope))
    app.add_handler(CallbackQueryHandler(rps_callback, pattern="^rps_"))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    print("✅ ربات روشنه!")
    app.run_polling()

if __name__ == "__main__":
    main()
