import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from pdf_processor import process_pdf

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# Set a higher log level for httpx to avoid spamming logs unless there are issues
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /start command.
    """
    await update.message.reply_text(
        "👋 Welcome! Send me a 'two-up' PDF (where two book pages are on one landscape sheet).\n\n"
        "I will:\n"
        "1. Split each page vertically into two.\n"
        "2. Compress the output for portability.\n"
        "3. Return the optimized PDF to you.\n\n"
        "Note: Maximum file size is 20MB (Telegram Bot API limit)."
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming PDF documents.
    """
    document = update.message.document

    if not document:
        return

    # Check if the file is a PDF
    if document.mime_type != "application/pdf" and not document.file_name.lower().endswith(".pdf"):
        await update.message.reply_text("❌ Please send a valid PDF document.")
        return

    # Check Telegram's 20MB download limit for bots (API restriction)
    if document.file_size > 20 * 1024 * 1024:
        await update.message.reply_text("⚠️ File is too large! I can only download PDFs up to 20MB via the standard Bot API.")
        return

    # Provide feedback to the user
    status_msg = await update.message.reply_text("📥 Downloading and processing your PDF... Please wait.")

    # Define temporary file paths
    file_id = document.file_id
    user_id = update.effective_user.id
    input_filename = f"in_{user_id}_{file_id}.pdf"
    output_filename = f"out_{user_id}_{file_id}.pdf"

    try:
        # Download the file
        file_obj = await document.get_file()
        await file_obj.download_to_drive(input_filename)

        # Process the PDF in a separate thread to avoid blocking the event loop
        # This prevents "Timed out" errors during CPU-intensive tasks
        success = await asyncio.to_thread(process_pdf, input_filename, output_filename)

        if success:
            # Send the processed PDF back
            with open(output_filename, 'rb') as pdf_file:
                await update.message.reply_document(
                    document=pdf_file,
                    filename=f"split_{document.file_name}",
                    caption="✅ Here is your split and compressed PDF!"
                )
        else:
            await update.message.reply_text("❌ Failed to process the PDF. It might be encrypted, password-protected, or corrupted.")

    except asyncio.TimeoutError:
        logger.error("Timeout occurred while processing document.")
        await update.message.reply_text("🛑 Processing took too long. The file might be too complex.")
    except Exception as e:
        logger.error(f"Error handling document: {e}")
        await update.message.reply_text("🛑 An unexpected error occurred while processing your file.")

    finally:
        # Clean up temporary files
        for filename in [input_filename, output_filename]:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except Exception as cleanup_err:
                    logger.error(f"Failed to delete {filename}: {cleanup_err}")

        # Try to delete the status message
        try:
            await status_msg.delete()
        except:
            pass

def main():
    """
    Initialize and run the bot.
    """
    if not TOKEN:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment variables.")
        print("Error: TELEGRAM_BOT_TOKEN is missing. Please check your .env file.")
        return

    # Increased timeouts for more stable file handling on slower connections
    application = ApplicationBuilder().token(TOKEN).read_timeout(30).write_timeout(30).connect_timeout(30).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.PDF, handle_document))

    # Run the bot
    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
