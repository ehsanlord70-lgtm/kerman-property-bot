
import os
import logging
import asyncio

from telegram import Update
from telegram.error import RetryAfter
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏠 ربات شکار ملک کرمان فعال شد!\n\n"
        "دستورات:\n"
        "/setprice 2000 5000\n"
        "/setarea 100 180\n"
        "/setneighborhood هزار و یک شب\n"
        "/status\n"
        "/help"
    )

async def setprice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        minimum, maximum = map(int, context.args)
        if minimum < 0 or maximum < minimum:
            raise ValueError()

        context.user_data["price"] = (minimum, maximum)
        await update.message.reply_text(
            f"قیمت ثبت شد: {minimum} تا {maximum} میلیارد تومان"
        )
    except (ValueError, TypeError):
        await update.message.reply_text("مثال: /setprice 2000 5000")

async def setarea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        minimum, maximum = map(int, context.args)
        if minimum <= 0 or maximum < minimum:
            raise ValueError()

        context.user_data["area"] = (minimum, maximum)
        await update.message.reply_text(
            f"متراژ ثبت شد: {minimum} تا {maximum} متر"
        )
    except (ValueError, TypeError):
        await update.message.reply_text("مثال: /setarea 100 180")

async def setneighborhood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    neighborhood = " ".join(context.args).strip()

    if not neighborhood:
        await update.message.reply_text(
            "مثال: /setneighborhood هزار و یک شب"
        )
        return

    context.user_data["neighborhood"] = neighborhood
    await update.message.reply_text(f"محله ثبت شد: {neighborhood}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data

    await update.message.reply_text(
        f"قیمت: {data.get('price', 'تعیین نشده')}\n"
        f"متراژ: {data.get('area', 'تعیین نشده')}\n"
        f"محله: {data.get('neighborhood', 'تعیین نشده')}"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

async def initialize_with_retry(app):
    for attempt in range(5):
        try:
            await app.initialize()
            logging.info("Telegram connection initialized successfully.")
            return

        except RetryAfter as error:
            wait_time = float(error.retry_after) + 5

            logging.warning(
                "Telegram rate limit. Waiting %.1f seconds. Attempt %s/5",
                wait_time,
                attempt + 1
            )

            await asyncio.sleep(wait_time)

    raise RuntimeError("Telegram initialization failed after 5 attempts.")

async def main():
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise RuntimeError("BOT_TOKEN تنظیم نشده است.")

    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("setprice", setprice))
    app.add_handler(CommandHandler("setarea", setarea))
    app.add_handler(CommandHandler("setneighborhood", setneighborhood))
    app.add_handler(CommandHandler("status", status))

    await initialize_with_retry(app)

    await app.start()
    await app.updater.start_polling()

    logging.info("Kerman Property Hunter is running.")

    try:
        await asyncio.Event().wait()
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
