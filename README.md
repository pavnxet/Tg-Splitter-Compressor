# 📖 Automated PDF Splitter & Compressor Telegram Bot

A specialized Telegram Bot designed to process "two-up" PDF documents (where two physical pages appear on a single digital landscape page). It automatically bisects each page and applies stream-level compression.

---

## ✨ Features

- **Vertical Bisection:** Automatically splits landscape pages exactly down the middle.
- **Sequential Ordering:** Ensures logical flow (Page 1 Left → Page 1 Right → Page 2 Left...).
- **Aggressive Compression:** Optimizes output by removing redundant objects and compressing streams.
- **Privacy-First:** Strict "clean as you go" policy for the server’s file system.

---

## 🛠️ Requirements

- **Python 3.10+**
- **PyMuPDF (fitz):** For high-performance PDF manipulation.
- **python-telegram-bot (v20+):** For asynchronous bot interactions.
- **python-dotenv:** For managing environment variables.

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd tg-pdf-splitter-bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file in the root directory:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### 4. Run the Bot
```bash
python bot.py
```

---

## 🔧 Deployment

For production, it is recommended to use a process manager like **PM2** or a **systemd** service.

### Example with PM2:
```bash
pm2 start bot.py --name "pdf-splitter-bot" --interpreter python3
```

---

## 🛡️ Limitations

- **File Size:** The bot can handle PDFs up to **20MB** due to Telegram Bot API download limits.
- **Encryption:** Password-protected or encrypted PDFs cannot be processed.

---

## 📜 License
This project is licensed under the MIT License.
