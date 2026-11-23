
import os
import logging
from telegram import Update
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
        "/setprice 2000 5000  قیمت از ۲ تا ۵ میلیارد\n"
        "/setarea 100 180  متراژ از ۱۰۰ تا ۱۸۰\n"
        "/setneighborhood هزار و یک شب  تعیین محله\n"
        "/status  مشاهده فیلترها\n"
        "/help  راهنما"
    )

async def setprice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        minimum, maximum = map(int, context.args)
        if minimum < 0 or maximum < minimum:
            raise ValueError()
        context.user_data["price"] = (minimum, maximum)
        await update.message.reply_text(
            f"✅ بازه قیمت ثبت شد: {minimum} تا {maximum} میلیارد تومان"
        )
    except (ValueError, TypeError):
        await update.message.reply_text(
            "فرمت درست:\n/setprice 2000 5000"
        )

async def setarea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        minimum, maximum = map(int, context.args)
        if minimum <= 0 or maximum < minimum:
            raise ValueError()
        context.user_data["area"] = (minimum, maximum)
        await update.message.reply_text(
            f"✅ متراژ ثبت شد: {minimum} تا {maximum} متر"
        )
    except (ValueError, TypeError):
        await update.message.reply_text(
            "فرمت درست:\n/setarea 100 180"
        )

async def setneighborhood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    neighborhood = " ".join(context.args).strip()
    if not neighborhood:
        await update.message.reply_text(
            "مثال:\n/setneighborhood هزار و یک شب"
        )
        return

    context.user_data["neighborhood"] = neighborhood
    await update.message.reply_text(
        f"✅ محله انتخابی: {neighborhood}"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    price = data.get("price", "تعیین نشده")
    area = data.get("area", "تعیین نشده")
    neighborhood = data.get("neighborhood", "تعیین نشده")

    await update.message.reply_text(
        "📋 فیلترهای جستجوی شما:\n\n"
        f"💰 قیمت: {price}\n"
        f"📐 متراژ: {area}\n"
        f"📍 محله: {neighborhood}\n\n"
        "برای تغییر هر فیلتر، دستور مربوطه را بفرست."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)

def main():
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

    print("Property bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
