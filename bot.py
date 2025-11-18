import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

ALLOWED_CHAT_IDS = { }  # Add your group ID here to restrict

if not OPENAI_API_KEY or not TELEGRAM_TOKEN:
    raise RuntimeError("Missing OPENAI_API_KEY or TELEGRAM_TOKEN env vars")

def ask_openai(message: str) -> str:
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Blunt ruthless AI. No sugarcoating. Keep it short."},
                {"role": "user", "content": message},
            ],
        },
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("AI bot online.")

async def handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if ALLOWED_CHAT_IDS and update.message.chat.id not in ALLOWED_CHAT_IDS:
        return

    user_text = update.message.text
    try:
        reply = ask_openai(user_text)
    except Exception as e:
        reply = f"Error: {e}"
    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
    app.run_polling()

if __name__ == "__main__":
    main()
