"""
ربات تلگرام هوشمند
نیازمندی‌ها:
pip install python-telegram-bot anthropic yt-dlp spotipy python-dotenv
"""

import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
import anthropic
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

# ─── تنظیمات ───────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN  = os.getenv("TELEGRAM_TOKEN")
ANTHROPIC_KEY   = os.getenv("ANTHROPIC_API_KEY")
SPOTIFY_ID      = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET  = os.getenv("SPOTIFY_CLIENT_SECRET")

# state های مکالمه
MAIN_MENU   = 0
AI_CHAT     = 1
MUSIC_SEARCH = 2
MUSIC_ARTIST = 3

# ─── کلاینت‌ها ─────────────────────────────────────────
claude_client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_ID,
        client_secret=SPOTIFY_SECRET
    )
)

# ذخیره تاریخچه چت به ازای هر کاربر
chat_histories: dict[int, list] = {}


# ══════════════════════════════════════════════════════
#  منوی اصلی
# ══════════════════════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🤖 چت با هوش مصنوعی", callback_data="menu_ai")],
        [InlineKeyboardButton("🎵 جستجو و دانلود آهنگ",  callback_data="menu_music")],
        [InlineKeyboardButton("ℹ️ راهنما",               callback_data="menu_help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "👋 سلام! به ربات هوشمند خوش اومدی.\n\n"
        "از منوی زیر یه بخش رو انتخاب کن:"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    return MAIN_MENU


# ══════════════════════════════════════════════════════
#  هوش مصنوعی
# ══════════════════════════════════════════════════════
async def ai_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🔙 برگشت به منوی اصلی", callback_data="back_main")]]
    await query.edit_message_text(
        "🤖 *بخش هوش مصنوعی*\n\n"
        "پیامت رو بنویس، Claude بهت جواب میده.\n"
        "برای شروع مجدد بنویس: /reset",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return AI_CHAT


async def ai_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    if user_text == "/reset":
        chat_histories[user_id] = []
        await update.message.reply_text("✅ تاریخچه چت پاک شد!")
        return AI_CHAT

    # اضافه کردن پیام کاربر به تاریخچه
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    chat_histories[user_id].append({"role": "user", "content": user_text})

    # نمایش ... در حین پردازش
    thinking_msg = await update.message.reply_text("⏳ در حال پردازش...")

    try:
        response = claude_client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system="تو یه دستیار هوشمند فارسی‌زبان هستی. جواب‌هات رو به فارسی بده مگه اینکه کاربر به زبان دیگه‌ای بنویسه.",
            messages=chat_histories[user_id]
        )
        assistant_reply = response.content[0].text

        # اضافه کردن جواب به تاریخچه
        chat_histories[user_id].append({"role": "assistant", "content": assistant_reply})

        await thinking_msg.edit_text(f"🤖 {assistant_reply}")

    except Exception as e:
        logger.error(f"Claude error: {e}")
        await thinking_msg.edit_text("❌ خطایی رخ داد. دوباره امتحان کن.")

    return AI_CHAT


# ══════════════════════════════════════════════════════
#  بخش موسیقی
# ══════════════════════════════════════════════════════
async def music_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🔍 جستجوی آهنگ",     callback_data="music_song")],
        [InlineKeyboardButton("🎤 آهنگ‌های خواننده", callback_data="music_artist")],
        [InlineKeyboardButton("🔙 برگشت",            callback_data="back_main")],
    ]
    await query.edit_message_text(
        "🎵 *بخش موسیقی*\n\nچی می‌خوای؟",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU


async def music_song_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["music_mode"] = "song"
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="menu_music")]]
    await query.edit_message_text(
        "🔍 اسم آهنگ رو بنویس:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MUSIC_SEARCH


async def music_artist_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["music_mode"] = "artist"
    keyboard = [[InlineKeyboardButton("🔙 برگشت", callback_data="menu_music")]]
    await query.edit_message_text(
        "🎤 اسم خواننده رو بنویس:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MUSIC_SEARCH


async def music_search_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = update.message.text
    mode = context.user_data.get("music_mode", "song")

    searching_msg = await update.message.reply_text("🔍 در حال جستجو...")

    try:
        if mode == "song":
            results = sp.search(q=query_text, type="track", limit=5)
            tracks = results["tracks"]["items"]

            if not tracks:
                await searching_msg.edit_text("❌ آهنگی پیدا نشد!")
                return MUSIC_SEARCH

            keyboard = []
            for i, track in enumerate(tracks):
                name = track["name"]
                artist = track["artists"][0]["name"]
                # ذخیره اطلاعات آهنگ
                context.user_data[f"track_{i}"] = {
                    "name": name,
                    "artist": artist,
                    "query": f"{artist} {name}"
                }
                keyboard.append([
                    InlineKeyboardButton(
                        f"🎵 {name} - {artist}",
                        callback_data=f"download_{i}"
                    )
                ])

            keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="menu_music")])
            await searching_msg.edit_text(
                "نتایج جستجو:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif mode == "artist":
            results = sp.search(q=query_text, type="artist", limit=1)
            artists = results["artists"]["items"]

            if not artists:
                await searching_msg.edit_text("❌ خواننده‌ای پیدا نشد!")
                return MUSIC_SEARCH

            artist_id = artists[0]["id"]
            artist_name = artists[0]["name"]
            top_tracks = sp.artist_top_tracks(artist_id, country="US")["tracks"][:8]

            keyboard = []
            for i, track in enumerate(top_tracks):
                name = track["name"]
                context.user_data[f"track_{i}"] = {
                    "name": name,
                    "artist": artist_name,
                    "query": f"{artist_name} {name}"
                }
                keyboard.append([
                    InlineKeyboardButton(
                        f"🎵 {name}",
                        callback_data=f"download_{i}"
                    )
                ])

            keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="menu_music")])
            await searching_msg.edit_text(
                f"🎤 آهنگ‌های برتر {artist_name}:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    except Exception as e:
        logger.error(f"Spotify error: {e}")
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

    await query.edit_message_text(f"⬇️ در حال دانلود:\n🎵 {track_info['name']} - {track_info['artist']}")

    try:
        search_query = f"ytsearch1:{track_info['query']} official audio"
        output_path = f"/tmp/{track_info['name'][:30]}.mp3"

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path.replace(".mp3", ""),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([search_query])

        # ارسال فایل
        with open(output_path, "rb") as audio_file:
            await context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=audio_file,
                title=track_info["name"],
                performer=track_info["artist"],
                caption=f"🎵 {track_info['name']}\n🎤 {track_info['artist']}"
            )

        # پاک کردن فایل موقت
        os.remove(output_path)

    except Exception as e:
        logger.error(f"Download error: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ خطا در دانلود. آهنگ رو در یوتیوب پیدا نکردم."
        )

    return MUSIC_SEARCH


# ══════════════════════════════════════════════════════
#  راهنما
# ══════════════════════════════════════════════════════
async def help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [[InlineKeyboardButton("🔙 برگشت به منو", callback_data="back_main")]]
    await query.edit_message_text(
        "ℹ️ *راهنمای ربات*\n\n"
        "🤖 *هوش مصنوعی:* با Claude چت کن، هر سوالی داری بپرس\n\n"
        "🎵 *موسیقی:*\n"
        "  • جستجوی آهنگ: اسم آهنگ رو بنویس\n"
        "  • خواننده: اسم خواننده رو بنویس، لیست آهنگ‌هاش میاد\n\n"
        "📌 *دستورات:*\n"
        "  /start - شروع مجدد\n"
        "  /reset - پاک کردن تاریخچه چت",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return MAIN_MENU


# ══════════════════════════════════════════════════════
#  callback برگشت
# ══════════════════════════════════════════════════════
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "back_main":
        return await start(update, context)
    elif data == "menu_ai":
        return await ai_menu(update, context)
    elif data == "menu_music":
        return await music_menu(update, context)
    elif data == "menu_help":
        return await help_menu(update, context)
    elif data == "music_song":
        return await music_song_prompt(update, context)
    elif data == "music_artist":
        return await music_artist_prompt(update, context)
    elif data.startswith("download_"):
        return await download_track(update, context)


# ══════════════════════════════════════════════════════
#  اجرای ربات
# ══════════════════════════════════════════════════════
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [
                CallbackQueryHandler(button_handler),
            ],
            AI_CHAT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat_handler),
                CallbackQueryHandler(button_handler),
            ],
            MUSIC_SEARCH: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, music_search_handler),
                CallbackQueryHandler(button_handler),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)

    logger.info("ربات شروع به کار کرد!")

    WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # آدرس Koyeb تو

    if WEBHOOK_URL:
        # حالت Webhook برای Koyeb
        app.run_webhook(
            listen="0.0.0.0",
            port=int(os.getenv("PORT", 8000)),
            webhook_url=WEBHOOK_URL,
        )
    else:
        # حالت Polling برای تست لوکال
        app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
