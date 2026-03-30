import os
import io
import datetime
import logging
import tempfile, os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    filters, ContextTypes
)
from invoice_generator import generate_invoice
from db import save_customer, get_all_customers, get_customer, update_payment_status

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
"8336408376:AAF_JV28fcAUBEDV5eIvswms1U4OmjDiefU"
# ── PASTE YOUR NEW BOT TOKEN HERE ─────────────────────────────────────────────
BOT_TOKEN = os.environ.get("8336408376:AAF_JV28fcAUBEDV5eIvswms1U4OmjDiefU"
, "")# ─────────────────────────────────────────────────────────────────────────────

MAIN_MENU = [["📄 New Invoice"], ["📋 All Customers", "🔍 Find Customer"], ["✅ Mark Paid"]]

NAME, CUSTOMER_ID, ITEM, AMOUNT, PAYMENT_STATUS, DELIVERY_DATE, DELIVERY_TIME, CAR_IMAGE = range(8)
SEARCHING, MARKING = range(8, 10)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to *BORIS OG STORE* Invoice Bot!\n\nChoose an option below:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    )

async def new_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "📝 *New Invoice — Step 1/7*\n\nEnter customer *name*:",
        parse_mode="Markdown", reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text.strip()
    await update.message.reply_text("🆔 *Step 2/7* — Enter customer *ID*:", parse_mode="Markdown")
    return CUSTOMER_ID

async def get_customer_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['customer_id'] = update.message.text.strip()
    await update.message.reply_text("🎮 *Step 3/7* — Enter *item name*:\n_(e.g. In-Game Car Account)_", parse_mode="Markdown")
    return ITEM

async def get_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['item'] = update.message.text.strip()
    await update.message.reply_text("💰 *Step 4/7* — Enter *amount* (e.g. 10500):", parse_mode="Markdown")
    return AMOUNT

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['amount'] = update.message.text.strip()
    keyboard = [["✅ Paid", "⏳ Pending"]]
    await update.message.reply_text(
        "💳 *Step 5/7* — Payment status?",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return PAYMENT_STATUS

async def get_payment_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['paid'] = "paid" if "Paid" in update.message.text else "pending"
    keyboard = [["⏳ Pending / TBD"]]
    await update.message.reply_text(
        "📅 *Step 6/7* — Enter *delivery date*\n_(e.g. 31 March 2026)_\nor tap Pending:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return DELIVERY_DATE

async def get_delivery_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    context.user_data['delivery_date'] = "Pending" if "Pending" in text else text
    keyboard = [["⏳ Pending / TBD"]]
    await update.message.reply_text(
        "⏰ *Step 7/7* — Enter *delivery time*\n_(e.g. Before 1:00 PM)_\nor tap Pending:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return DELIVERY_TIME

async def get_delivery_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    context.user_data['delivery_time'] = "Pending" if "Pending" in text else text
    await update.message.reply_text(
        "🚗 Send the *car image* (photo)\nor type /skip to skip image:",
        parse_mode="Markdown", reply_markup=ReplyKeyboardRemove()
    )
    return CAR_IMAGE

async def get_car_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        image_path = os.path.join(tempfile.gettempdir(), f"car_{context.user_data['customer_id']}.jpg")
        await file.download_to_drive(image_path)
        context.user_data['image_path'] = image_path
    return await finalize_invoice(update, context)

async def skip_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['image_path'] = None
    return await finalize_invoice(update, context)

async def finalize_invoice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    await update.message.reply_text("⏳ Generating invoice...", reply_markup=ReplyKeyboardRemove())
    try:
        pdf_bytes = generate_invoice(
            name=data.get('name'),
            customer_id=data.get('customer_id'),
            item=data.get('item'),
            amount=data.get('amount'),
            paid=data.get('paid', 'pending'),
            delivery_date=data.get('delivery_date', 'Pending'),
            delivery_time=data.get('delivery_time', 'Pending'),
            image_path=data.get('image_path'),
        )
        save_customer({
            'name': data.get('name'),
            'customer_id': data.get('customer_id'),
            'item': data.get('item'),
            'amount': data.get('amount'),
            'paid': data.get('paid', 'pending'),
            'delivery_date': data.get('delivery_date', 'Pending'),
            'delivery_time': data.get('delivery_time', 'Pending'),
            'created_at': datetime.datetime.now().isoformat(),
        })
        paid_text = "✅ PAID IN FULL" if data.get('paid') == 'paid' else "⏳ PAYMENT PENDING"
        caption = (
            f"🧾 *Invoice Generated!*\n\n"
            f"👤 *{data.get('name')}*\n"
            f"🆔 `{data.get('customer_id')}`\n"
            f"🎮 {data.get('item')}\n"
            f"💰 RS {data.get('amount')}\n"
            f"💳 {paid_text}\n"
            f"📅 {data.get('delivery_date')}  {data.get('delivery_time')}"
        )
        await update.message.reply_document(
            document=io.BytesIO(pdf_bytes),
            filename=f"Invoice_{data.get('name')}.pdf",
            caption=caption,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Invoice error: {e}")
        await update.message.reply_text(f"❌ Error generating invoice: {e}")

    await update.message.reply_text("✅ Done! What's next?",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True))
    return ConversationHandler.END

async def all_customers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    customers = get_all_customers()
    if not customers:
        await update.message.reply_text("📭 No customers saved yet.")
        return
    msg = "📋 *All Customers (latest 15):*\n\n"
    for c in customers[-15:]:
        icon = "✅" if c.get('paid') == 'paid' else "⏳"
        msg += f"{icon} *{c['name']}* | `{c['customer_id']}` | RS {c['amount']}\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def find_customer_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Enter customer *name or ID*:",
        parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    return SEARCHING

async def find_customer_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = get_customer(update.message.text.strip())
    if not results:
        await update.message.reply_text("❌ No customer found.")
    else:
        for c in results:
            status = "✅ PAID" if c.get('paid') == 'paid' else "⏳ PENDING"
            await update.message.reply_text(
                f"👤 *{c['name']}*\n🆔 `{c['customer_id']}`\n🎮 {c['item']}\n"
                f"💰 RS {c['amount']}\n💳 {status}\n"
                f"📅 {c.get('delivery_date','—')}  {c.get('delivery_time','')}\n"
                f"🕒 {c.get('created_at','')[:10]}",
                parse_mode="Markdown"
            )
    await update.message.reply_text("What's next?",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True))
    return ConversationHandler.END

async def mark_paid_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Enter the customer *ID* to mark as paid:",
        parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    return MARKING

async def mark_paid_do(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = update.message.text.strip()
    if update_payment_status(cid, 'paid'):
        await update.message.reply_text(f"✅ Customer `{cid}` marked as *PAID*!", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ ID `{cid}` not found.", parse_mode="Markdown")
    await update.message.reply_text("What's next?",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True))
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Cancelled.",
        reply_markup=ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True))
    return ConversationHandler.END

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    invoice_conv = ConversationHandler(
        entry_points=[
            CommandHandler("newinvoice", new_invoice),
            MessageHandler(filters.Regex("^📄 New Invoice$"), new_invoice),
        ],
        states={
            NAME:           [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            CUSTOMER_ID:    [MessageHandler(filters.TEXT & ~filters.COMMAND, get_customer_id)],
            ITEM:           [MessageHandler(filters.TEXT & ~filters.COMMAND, get_item)],
            AMOUNT:         [MessageHandler(filters.TEXT & ~filters.COMMAND, get_amount)],
            PAYMENT_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_payment_status)],
            DELIVERY_DATE:  [MessageHandler(filters.TEXT & ~filters.COMMAND, get_delivery_date)],
            DELIVERY_TIME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, get_delivery_time)],
            CAR_IMAGE: [
                MessageHandler(filters.PHOTO, get_car_image),
                CommandHandler("skip", skip_image),
                MessageHandler(filters.TEXT & ~filters.COMMAND, skip_image),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    find_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🔍 Find Customer$"), find_customer_prompt)],
        states={SEARCHING: [MessageHandler(filters.TEXT & ~filters.COMMAND, find_customer_search)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    mark_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^✅ Mark Paid$"), mark_paid_prompt)],
        states={MARKING: [MessageHandler(filters.TEXT & ~filters.COMMAND, mark_paid_do)]},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(invoice_conv)
    app.add_handler(find_conv)
    app.add_handler(mark_conv)
    app.add_handler(MessageHandler(filters.Regex("^📋 All Customers$"), all_customers))

    logger.info("🤖 BORIS OG STORE Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    main()
