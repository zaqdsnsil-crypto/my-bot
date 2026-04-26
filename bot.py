import os
import logging
import random
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

MAIN_MENU = 0
MUSIC_SEARCH = 1

main_keyboard = ReplyKeyboardMarkup([
    ["🎵 جستجو و دانلود آهنگ", "🎤 آهنگ‌های خواننده"],
    ["🏙️ شهری بازی", "❤️ خاطرات عشق"],
    ["😢 روزهای تنها", "🤖 مدیریت گروه"],
    ["🎉 سرگرمی", "📖 رمان"],
    ["🎵 موزیک دلخواه"]
], resize_keyboard=True, one_time_keyboard=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎵 جستجو و دانلود آهنگ", callback_data="menu_music")],
        [InlineKeyboardButton("🎤 جستجوی خواننده", callback_data="menu_artist")],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data="menu_help")],
    ]
    text = "👋 سلام! به ربات موسیقی خوش اومدی.\n\nاز منوی زیر انتخاب کن:"
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    return MAIN_MENU

async def music_song_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["music_mode"] = "song"
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]]
    await query.edit_message_text("🔍 اسم آهنگ رو بنویس:", reply_markup=InlineKeyboardMarkup(keyboard))
    return MUSIC_SEARCH

async def music_artist_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["music_mode"] = "artist"
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]]
    await query.edit_message_text("🎤 اسم خواننده رو بنویس:", reply_markup=InlineKeyboardMarkup(keyboard))
    return MUSIC_SEARCH

async def music_search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = update.message.text
    mode = context.user_data.get("music_mode", "song")
    searching_msg = await update.message.reply_text("🔍 در حال جستجو...")

    try:
        if mode == "song":
            search_query = f"ytsearch5:{query_text}"
        else:
            search_query = f"ytsearch5:{query_text} official audio"

        ydl_opts = {
            "quiet": True,
            "extract_flat": True,
            "default_search": "ytsearch5",
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(search_query, download=False)

        if not results or "entries" not in results or not results["entries"]:
            await searching_msg.edit_text("❌ چیزی پیدا نشد!")
            return MUSIC_SEARCH

        keyboard = []
        for i, entry in enumerate(results["entries"][:5]):
            title = entry.get("title", "نامشخص")[:50]
            url = entry.get("url") or entry.get("webpage_url", "")
            context.user_data[f"track_{i}"] = {"title": title, "url": url}
            keyboard.append([InlineKeyboardButton(f"🎵 {title}", callback_data=f"download_{i}")])

        keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="back_main")])
        await searching_msg.edit_text("نتایج جستجو:", reply_markup=InlineKeyboardMarkup(keyboard))

    except Exception as e:
        logger.error(f"Search error: {e}")
        await searching_msg.edit_text("❌ خطا در جستجو. دوباره امتحان کن.")

    return MUSIC_SEARCH

async def download_track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    track_index = int(query.data.split("_")[1])
    track_info = context.user_data.get(f"track_{track_index}")

    if not track_info:
        await query.edit_message_text("❌ اطلاعات آهنگ پیدا نشد!")
        return MUSIC_SEARCH

    await query.edit_message_text(f"⬇️ در حال دانلود:\n🎵 {track_info['title']}")

    try:
        safe_name = "".join(c for c in track_info['title'][:30] if c.isalnum() or c in " _-")
        output_path = f"/tmp/{safe_name}.%(ext)s"
        mp3_path = f"/tmp/{safe_name}.mp3"

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path,
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([track_info["url"]])

        with open(mp3_path, "rb") as audio_file:
            await context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=audio_file,
                title=track_info["title"],
                caption=f"🎵 {track_info['title']}"
            )
        os.remove(mp3_path)

    except Exception as e:
        logger.error(f"Download error: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ خطا در دانلود.")

    return MUSIC_SEARCH

async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="back_main")]]
    await query.edit_message_text(
        "ℹ️ *راهنما*\n\n🎵 جستجوی آهنگ: اسم آهنگ رو بنویس\n🎤 خواننده: اسم خواننده رو بنویس",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "back_main":
        return await start(update, context)
    elif data == "menu_music":
        return await music_song_prompt(update, context)
    elif data == "menu_artist":
        return await music_artist_prompt(update, context)
    elif data == "menu_help":
        return await help_menu(update, context)
    elif data.startswith("download_"):
        return await download_track(update, context)

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "🏙️ شهری بازی":
        await update.message.reply_text(
            "🏙️ بازی شهری شروع شد!\n\nیک شهر خیالی انتخاب کن:\n• تهران\n• مشهد\n• اصفهان\n• شیراز\n• تبریز\n\nبه زودی نسخه کامل بازی اضافه می‌شود 🎮",
            reply_markup=main_keyboard
        )
    elif text == "❤️ خاطرات عشق":
        memories = [
            "💕 یادته اولین بار که دیدمت چقدر قلبم تند زد؟",
            "❤️ تو بهترین اتفاق زندگی من بودی...",
            "🌹 حتی تو روزای بارونی، فکر تو آسمونمو آفتابی می‌کرد.",
            "💌 اگه یه پیام به گذشته بفرستم، فقط می‌گم: اونو بیشتر دوست داشته باش"
        ]
        await update.message.reply_text(random.choice(memories), reply_markup=main_keyboard)
    elif text == "😢 روزهای تنها":
        lonely_replies = [
            "🌧️ گاهی تنهایی قشنگه... چون بیشتر به خودت فکر می‌کنی.",
            "😔 تو تنها نیستی، من اینجام که باهات حرف بزنم.",
            "🌙 شب‌ها سخت‌ترین وقته... ولی فردا همیشه بهتره.",
            "🫂 بگو چی تو دلته؟ من گوش می‌دم."
        ]
        await update.message.reply_text(random.choice(lonely_replies), reply_markup=main_keyboard)
    elif text == "🤖 مدیریت گروه":
        await update.message.reply_text(
            "👥 مدیریت گروه\n\nقابلیت‌های فعال:\n• خوش‌آمدگویی جدید اعضا\n• حذف پیام‌های اسپم\n\nبرای فعال کردن، منو به گروه اضافه کن و /admin بزن.",
            reply_markup=main_keyboard
        )
    elif text == "🎉 سرگرمی":
        await update.message.reply_text(
            "🎉 سرگرمی‌های فعال:\n\n• جوک بگو\n• معما بده\n• تست شخصیت\n• سنگ کاغذ قیچی",
            reply_markup=main_keyboard
        )
    elif text == "📖 رمان":
        stories = [
            "📖 رمان کوتاه:\nدخترکی تو ایستگاه قطار منتظر کسی بود که هیچ‌وقت نیومد...",
            "📚 داستان:\nیه پسر هر شب به آسمان نگاه می‌کرد و ستاره‌ای رو پیدا کرد که فقط مال اون بود.",
            "🌹 یه روز یه دختر عاشق شد... ولی نه از یه نفر، از سکوت شب‌ها."
        ]
        await update.message.reply_text(random.choice(stories) + "\n\nادامه‌ش رو می‌خوای؟", reply_markup=main_keyboard)
    elif text == "🎵 موزیک دلخواه":
        await update.message.reply_text(
            "🎵 موزیک دلخواه\n\nاسم آهنگ یا خواننده مورد علاقه‌ت رو بنویس.",
            reply_markup=main_keyboard
        )
    else:
        await update.message.reply_text("❓ از منوی پایین یکی رو انتخاب کن.", reply_markup=main_keyboard)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [CallbackQueryHandler(button_handler)],
            MUSIC_SEARCH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, music_search_handler),
                CallbackQueryHandler(button_handler),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler))

    logger.info("ربات شروع به کار کرد!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
