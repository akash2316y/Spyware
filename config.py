import os
from dotenv import load_dotenv

load_dotenv()

# ── Telegram ──────────────────────────────────────────────
TELEGRAM_BOT_TOKEN  = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "")   # e.g. @mychannel or -100xxxxxxx
ADMIN_CHAT_ID       = os.getenv("ADMIN_CHAT_ID", "")          # your personal Telegram user ID
BOT_PASSWORD        = os.getenv("BOT_PASSWORD", "changeme123")

# ── Instagram ─────────────────────────────────────────────
INSTAGRAM_USERNAME  = os.getenv("INSTAGRAM_USERNAME", "")
TARGET_USERNAME     = os.getenv("TARGET_USERNAME", "")

# ── Monitor settings ──────────────────────────────────────
CHECK_INTERVAL      = int(os.getenv("CHECK_INTERVAL", "600"))  # seconds (600 = 10 min)

# ── Webhook server ────────────────────────────────────────
WEBHOOK_HOST        = os.getenv("WEBHOOK_HOST", "0.0.0.0")
WEBHOOK_PORT        = int(os.getenv("WEBHOOK_PORT", "5000"))
