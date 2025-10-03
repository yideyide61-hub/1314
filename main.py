import os
import threading
from fastapi import FastAPI
import uvicorn
from telegram import Update
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext

# -------------------- ENV VARIABLES --------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "7124683213"))
LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID", "7124683213"))

# -------------------- FASTAPI APP --------------------
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Bot is running on Render (PTB v13)!"}

@app.get("/ping")
def ping():
    return {"status": "alive"}

# -------------------- TELEGRAM BOT --------------------
def handle_new_chat_members(update: Update, context: CallbackContext):
    chat = update.effective_chat
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:  # Bot itself added
            adder = update.message.from_user
            log_message = (
                f"📢 Bot was added to a group!\n\n"
                f"👥 Group: {chat.title} (ID: {chat.id})\n"
                f"👤 Added by: {adder.first_name} {adder.last_name or ''} "
                f"(@{adder.username or 'NoUsername'})\n"
                f"🆔 User ID: {adder.id}"
            )
            context.bot.send_message(LOG_CHAT_ID, log_message)

            if adder.id != OWNER_ID:
                context.bot.send_message(
                    chat.id,
                    "⚠️ 您好，机器人已检测到加入了新群组，正在初始化新群组，请稍候..."
                )
                leave_message = (
                    f"🚪 Bot left a group!\n\n"
                    f"👥 Group: {chat.title} (ID: {chat.id})\n"
                    f"👤 Was added by: {adder.first_name} {adder.last_name or ''} "
                    f"(@{adder.username or 'NoUsername'})\n"
                    f"🆔 User ID: {adder.id}"
                )
                context.bot.send_message(LOG_CHAT_ID, leave_message)
                context.bot.leave_chat(chat.id)
            else:
                context.bot.send_message(chat.id, "✅ Bot initialized successfully.")

def run_telegram_bot():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, handle_new_chat_members))

    updater.start_polling()
    updater.idle()

# -------------------- ENTRY POINT --------------------
if __name__ == "__main__":
    # Run Telegram bot in separate thread
    threading.Thread(target=run_telegram_bot, daemon=True).start()

    # Run FastAPI (keeps Render alive & UptimeRobot ping works)
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
