# 📖 Automated PDF Splitter & Compressor Telegram Bot

A specialized Telegram Bot designed to process "two-up" PDF documents. Optimized for **Pure Python** environments like **Termux (Android)**.

---

## ✨ Features

- **Vertical Bisection:** Automatically splits landscape pages exactly down the middle.
- **Page Selection:** Extract and process specific page ranges (e.g., `1-5, 7, 10-12`).
- **Multiple Formats:** Choose output as optimized **PDF** or a **ZIP of JPEGs**.
- **Process Cancellation:** Easily cancel on-hold or running processes to reset state and clean up immediately.
- **Pure Python:** Highly portable, minimal system-level dependencies.
- **Privacy-First:** Strict "clean as you go" policy for the server’s file system.

---

## 🛠️ Requirements

- **Python 3.10+**
- **pypdf:** For Pure Python PDF manipulation.
- **python-telegram-bot (v20+):** For asynchronous bot interactions.
- **pdf2image & pillow:** For image conversion.
- **poppler (optional):** Required for PDF-to-Image conversion.

---

## 🚀 Quick Start

### 1. Clone and Install
```bash
git clone <repository-url>
cd tg-pdf-splitter-bot
pip install -r requirements.txt
```

### 2. Install Poppler (for image output)
- **Ubuntu/Linux:** `sudo apt install poppler-utils`
- **Mac (Homebrew):** `brew install poppler`
- **Termux:** `pkg install poppler`

### 3. Configure Environment
Create a `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 4. Run the Bot
```bash
python bot.py
```

---

## 🎮 How to Use

1. Send a PDF file to the bot.
2. The bot will ask for a **page range**. You can click the **❌ Cancel** button to abort at this stage.
   - Send `all` to process the entire document.
   - Send a range like `1-10` or `1, 3, 5-7`.
3. While the bot is downloading or processing the PDF, you can also click the **❌ Cancel** button to stop it.
4. Use **/settings** to toggle between PDF or Image output.

---

## 🛡️ Limitations
- **File Size:** PDFs up to **20MB** (Telegram Bot API download limit).
- **Encryption:** Password-protected PDFs cannot be processed.

---

## 📜 License
This project is licensed under the MIT License.
