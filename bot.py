import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from pdf_processor import process_pdf

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# User settings (in-memory for now, resets on bot restart)
user_settings = {} # {user_id: {"format": "pdf"}}
cancel_flags = {} # {user_id: bool}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /start command.
    """
    await update.message.reply_text(
        "👋 Welcome! Send me a 'two-up' PDF (where two book pages are on one landscape sheet).\n\n"
        "I will:\n"
        "1. Split each page vertically into two.\n"
        "2. Compress the output for portability.\n"
        "3. Return the optimized PDF or images to you.\n\n"
        "Commands:\n"
        "/settings - Choose output format (PDF or Images)\n"
        "After sending a PDF, you can specify a page range (e.g., '1-5, 7, 10-12' or 'all')."
    )

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Display settings menu.
    """
    user_id = update.effective_user.id
    current_format = user_settings.get(user_id, {}).get("format", "pdf")

    keyboard = [
        [
            InlineKeyboardButton(f"📄 PDF {'✅' if current_format == 'pdf' else ''}", callback_data="set_pdf"),
            InlineKeyboardButton(f"🖼️ Images {'✅' if current_format == 'images' else ''}", callback_data="set_images")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose your preferred output format:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle callback queries from settings buttons.
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id
    data = query.data

    if data == "cancel_process":
        cancel_flags[user_id] = True
        
        # Also clean up pending_pdf
        if 'pending_pdf' in context.user_data:
            del context.user_data['pending_pdf']
        if 'pdf_name' in context.user_data:
            del context.user_data['pdf_name']
            
        await query.edit_message_text("🚫 Process canceled. Send a new PDF to start over.")
        return

    if user_id not in user_settings:
        user_settings[user_id] = {"format": "pdf"}

    if data == "set_pdf":
        user_settings[user_id]["format"] = "pdf"
    elif data == "set_images":
        user_settings[user_id]["format"] = "images"

    # Update settings menu to show selection
    current_format = user_settings[user_id]["format"]
    keyboard = [
        [
            InlineKeyboardButton(f"📄 PDF {'✅' if current_format == 'pdf' else ''}", callback_data="set_pdf"),
            InlineKeyboardButton(f"🖼️ Images {'✅' if current_format == 'images' else ''}", callback_data="set_images")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"Output format set to: {current_format.upper()}", reply_markup=reply_markup)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming PDF documents.
    """
    document = update.message.document
    if not document: return

    # Some documents have mime_type="application/octet-stream" if not detected correctly
    if not (document.mime_type == "application/pdf" or document.file_name.lower().endswith(".pdf")):
        await update.message.reply_text("❌ Please send a valid PDF document.")
        return

    # Check Telegram's 20MB download limit for bots (API restriction)
    if document.file_size > 20 * 1024 * 1024:
        await update.message.reply_text("⚠️ File is too large! (Limit 20MB)")
        return

    # Store file info and wait for page range
    context.user_data['pending_pdf'] = document.file_id
    context.user_data['pdf_name'] = document.file_name

    cancel_flags[update.effective_user.id] = False
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_process")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📝 PDF received! Now, specify the page range you want to process (e.g., '1-5, 7, 10-12').\n\n"
        "👉 Send **'all'** to process the entire document.",
        reply_markup=reply_markup
    )

async def handle_page_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle text input representing the page range.
    """
    if 'pending_pdf' not in context.user_data:
        # Not expecting a range right now, ignore or send help
        return

    file_id = context.user_data.pop('pending_pdf')
    pdf_name = context.user_data.pop('pdf_name')
    page_range_text = update.message.text.strip().lower()

    page_range = None if page_range_text == "all" else page_range_text

    user_id = update.effective_user.id
    cancel_flags[user_id] = False
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_process")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    status_msg = await update.message.reply_text("📥 Downloading and processing your PDF... Please wait.", reply_markup=reply_markup)
    # Ensure temporary filenames are unique and cleaned up
    import uuid
    uid = str(uuid.uuid4())[:8]
    input_filename = f"in_{user_id}_{uid}.pdf"
    output_filename = f"out_{user_id}_{uid}.pdf"

    # Get user format preference
    output_format = user_settings.get(user_id, {}).get("format", "pdf")

    try:
        # Download the file
        file_obj = await context.bot.get_file(file_id)
        await file_obj.download_to_drive(input_filename)

        # Process the PDF in a separate thread
        success, result_path = await asyncio.to_thread(
            process_pdf, input_filename, output_filename, page_range, output_format, lambda: cancel_flags.get(user_id, False)
        )

        if cancel_flags.get(user_id, False):
            pass
        elif success:
            with open(result_path, 'rb') as f:
                if output_format == "pdf":
                    await update.message.reply_document(
                        document=f,
                        filename=f"split_{pdf_name}",
                        caption="✅ Here is your split and compressed PDF!"
                    )
                else:
                    await update.message.reply_document(
                        document=f,
                        filename=f"split_images_{pdf_name.replace('.pdf', '')}.zip",
                        caption="✅ Here is your split images (ZIP)!"
                    )
        else:
            await update.message.reply_text(f"❌ Failed to process PDF: {result_path}")

    except Exception as e:
        logger.error(f"Error handling document: {e}")
        await update.message.reply_text("🛑 An unexpected error occurred.")

    finally:
        # Clean up files
        for f in [input_filename, output_filename, output_filename.replace(".pdf", ".zip"), f"{output_filename}_tmp.pdf"]:
            if os.path.exists(f):
                try: os.remove(f)
                except: pass
        if not cancel_flags.get(user_id, False):
            try: await status_msg.delete()
            except: pass
        cancel_flags.pop(user_id, None)

def main():
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN missing.")
        return

    application = ApplicationBuilder().token(TOKEN).read_timeout(60).write_timeout(60).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("settings", settings))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    # Handle text only if we have a pending PDF
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_page_range))

    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
