import os
import logging
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SPOTIPY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")

MAIN_MENU = 0
MUSIC_SEARCH = 1

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET
    )
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎵 جستجو و دانلود آهنگ", callback_data="menu_music")],
        [InlineKeyboardButton("🎤 آهنگ‌های خواننده", callback_data="menu_artist")],
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
            results = sp.search(q=query_text, type="track", limit=5)
            tracks = results["tracks"]["items"]
            if not tracks:
                await searching_msg.edit_text("❌ آهنگی پیدا نشد!")
                return MUSIC_SEARCH
            keyboard = []
            for i, track in enumerate(tracks):
                name = track["name"]
                artist = track["artists"][0]["name"]
                context.user_data[f"track_{i}"] = {"name": name, "artist": artist, "query": f"{artist} {name}"}
                keyboard.append([InlineKeyboardButton(f"🎵 {name} - {artist}", callback_data=f"download_{i}")])
            keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="back_main")])
            await searching_msg.edit_text("نتایج جستجو:", reply_markup=InlineKeyboardMarkup(keyboard))
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
                context.user_data[f"track_{i}"] = {"name": name, "artist": artist_name, "query": f"{artist_name} {name}"}
                keyboard.append([InlineKeyboardButton(f"🎵 {name}", callback_data=f"download_{i}")])
            keyboard.append([InlineKeyboardButton("🔙 برگشت", callback_data="back_main")])
            await searching_msg.edit_text(f"🎤 آهنگ‌های برتر {artist_name}:", reply_markup=InlineKeyboardMarkup(keyboard))
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
        output_path = f"/tmp/{track_info['name'][:30]}.%(ext)s"
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path,
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([search_query])
        mp3_path = f"/tmp/{track_info['name'][:30]}.mp3"
        with open(mp3_path, "rb") as audio_file:
            await context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=audio_file,
                title=track_info["name"],
                performer=track_info["artist"],
                caption=f"🎵 {track_info['name']}\n🎤 {track_info['artist']}"
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
    logger.info("ربات شروع به کار کرد!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
