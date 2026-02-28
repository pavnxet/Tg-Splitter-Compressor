# 📖 Automated PDF Splitter & Compressor Telegram Bot

A specialized Telegram Bot designed to process "two-up" PDF documents. Optimized for **Pure Python** environments like **Termux (Android)**, making it highly portable and easy to install.

---

## ✨ Features

- **Vertical Bisection:** Automatically splits landscape pages exactly down the middle.
- **Sequential Ordering:** Ensures logical flow (Page 1 Left → Page 1 Right → Page 2 Left...).
- **Pure Python:** Uses `pypdf`, requiring zero C++ compilers or system-level dependencies.
- **Privacy-First:** Strict "clean as you go" policy for the server’s file system.

---

## 🛠️ Requirements

- **Python 3.10+**
- **pypdf:** For Pure Python PDF manipulation.
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

## 📱 Termux Installation (Android)
This bot is designed to work out-of-the-box in Termux:
```bash
pkg update && pkg upgrade
pkg install python
pip install -r requirements.txt
python bot.py
```

---

## 🔧 Deployment
For production, it is recommended to use a process manager like **PM2**.

```bash
pm2 start bot.py --name "pdf-splitter-bot" --interpreter python3
```

---

## 🛡️ Limitations
- **File Size:** The bot can handle PDFs up to **20MB** (Telegram Bot API download limit).
- **Encryption:** Password-protected PDFs cannot be processed.

---

## 📜 License
This project is licensed under the MIT License.
