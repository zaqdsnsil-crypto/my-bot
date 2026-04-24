
import os
TOKEN = os.environ.get("TOKEN")

from telegram import Update, ChatPermissions
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import datetime

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 سلام! من ربات مدیریت گروهم!\n\n"
        "دستورات:\n"
        "🚫 /ban - بن کردن\n"
        "✅ /unban - آنبن کردن\n"
        "🔇 /mute - میوت کردن\n"
        "🔊 /unmute - آنمیوت کردن\n"
        "👢 /kick - کیک کردن\n"
        "📌 /pin - پین کردن\n"
        "👤 /userinfo - اطلاعات کاربر\n"
    )

async def is_admin(update: Update) -> bool:
    user = update.message.from_user
    chat = update.message.chat
    member = await chat.get_member(user.id)
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
            ChatPermissions(can_send_messages=False), until_date=until
        )
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
            ChatPermissions(can_send_messages=True, can_send_photos=True, can_send_videos=True)
        )
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
        f"👤 اطلاعات کاربر:\n\n"
        f"📛 نام: {user.full_name}\n"
        f"🆔 آیدی: {user.id}\n"
        f"👤 یوزرنیم: @{user.username if user.username else 'ندارد'}"
    )

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
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    print("✅ ربات روشنه!")
    app.run_polling()

if __name__ == "__main__":
    main()
