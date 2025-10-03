import os
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

# Bot token and settings (from Render env vars)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "7124683213"))
LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID", "7124683213"))

async def handle_new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:  # Bot was added
            adder = update.message.from_user
            log_message = (
                f"📢 Bot was added to a group!\n\n"
                f"👥 Group: {chat.title} (ID: {chat.id})\n"
                f"👤 Added by: {adder.first_name} {adder.last_name or ''} (@{adder.username or 'NoUsername'})\n"
                f"🆔 User ID: {adder.id}"
            )
            await context.bot.send_message(LOG_CHAT_ID, log_message)

            if adder.id != OWNER_ID:
                await context.bot.send_message(chat.id, "⚠️ 您好，机器人已检测到加入了新群组，正在初始化新群组，请稍候...")
                leave_message = (
                    f"🚪 Bot left a group!\n\n"
                    f"👥 Group: {chat.title} (ID: {chat.id})\n"
                    f"👤 Was added by: {adder.first_name} {adder.last_name or ''} (@{adder.username or 'NoUsername'})\n"
                    f"🆔 User ID: {adder.id}"
                )
                await context.bot.send_message(LOG_CHAT_ID, leave_message)
                await context.bot.leave_chat(chat.id)
            else:
                await context.bot.send_message(chat.id, "✅ Bot initialized successfully.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_chat_members))

    # This will run polling (works fine on Render)
    app.run_polling()

if __name__ == "__main__":
    main()
