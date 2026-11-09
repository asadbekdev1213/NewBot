
import os
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from google import genai

# API keys from hosting environment
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN or not GEMINI_API_KEY:
    raise RuntimeError("API keys are missing!")

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-3.8-flash"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I'm Cleveron AI 🤖\n"
        "Ask me anything!"
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    question = update.message.text

    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=question
        )

        answer = response.text or "I couldn't generate an answer."

        # Telegram message length limit
        for i in range(0, len(answer), 4000):
            await update.message.reply_text(answer[i:i + 4000])

    except Exception:
        await update.message.reply_text(
            "Sorry, something went wrong. Please try again."
        )


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    print("Cleveron AI is running!")
    app.run_polling()


if __name__ == "__main__":
    main()
