
import os
import asyncio
import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from google import genai

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
RENDER_URL = os.environ["RENDER_EXTERNAL_URL"]

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-3.5-flash-lite"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! I'm Cleveron AI 🤖\nAsk me anything!"
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

        for i in range(0, len(answer), 4000):
            await update.message.reply_text(answer[i:i + 4000])

    except Exception:
        logging.exception("Gemini request failed")
        await update.message.reply_text(
            "Sorry, something went wrong. Please try again."
        )


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("Cleveron AI is starting...")

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
        url_path=BOT_TOKEN,
        webhook_url=f"{RENDER_URL}/{BOT_TOKEN}",
        allowed_updates=Update.ALL_TYPES,
    )


if __name__ == "__main__":
    main()
