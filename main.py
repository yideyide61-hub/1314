import os
import asyncio
from fastapi import FastAPI
import uvicorn
from telegram import Update
from telegram.ext import (
    Application,
    ContextTypes,
    MessageHandler,
    filters,
)

# -------------------- ENV VARIABLES --------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "7124683213"))
LOG_CHAT_ID = int(os.getenv("LOG_CHAT_ID", "7124683213"))

# -------------------- FASTAPI APP --------------------
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Bot is running on Render!"}

@app.get("/ping")
def ping():
    return {"status": "alive"}

# -------------------- TELEGRAM APP --------------------
telegram_app = Application.builder().token(BOT_TOKEN).build()

# --- Handlers ---
async def handle_new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:  # Bot added
            adder = update.message.from_user
            log_message = (
                f"📢 Bot was added to a group!\n\n"
                f"👥 Group: {chat.title} (ID: {chat.id})\n"
                f"👤 Added by: {adder.first_name} {adder.last_name or ''} "
                f"(@{adder.username or 'NoUsername'})\n"
                f"🆔 User ID: {adder.id}"
            )
            await context.bot.send_message(LOG_CHAT_ID, log_message)

            if adder.id != OWNER_ID:
                await context.bot.send_message(
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
                await context.bot.send_message(LOG_CHAT_ID, leave_message)
                await context.bot.leave_chat(chat.id)
            else:
                await context.bot.send_message(chat.id, "✅ Bot initialized successfully.")

telegram_app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_chat_members))

# -------------------- BACKGROUND BOT TASK --------------------
async def run_bot():
    """Run the Telegram bot in background forever"""
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()
    await asyncio.Event().wait()  # prevent exit

# -------------------- MAIN ENTRY --------------------
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())  # bot in background

    # Run FastAPI server (needed for Render + UptimeRobot)
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
