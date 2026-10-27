"""
run.py
------
Poora system ek saath start karo:
  1. Webhook server (Flask)  — port 5000
  2. Telegram bot (polling)  — main thread
"""

import logging
import threading
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
)
logger = logging.getLogger(__name__)

BANNER = """
╔══════════════════════════════════════════════╗
║     Instagram → Telegram Monitor System      ║
║          by misiektoja + custom bot          ║
╚══════════════════════════════════════════════╝
"""


def check_config():
    """Zaroori env variables check karo."""
    from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, BOT_PASSWORD
    errors = []
    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN missing")
    if not TELEGRAM_CHANNEL_ID:
        errors.append("TELEGRAM_CHANNEL_ID missing")
    if BOT_PASSWORD == "changeme123":
        logger.warning("⚠️  Default password in use — please change BOT_PASSWORD in .env")
    if errors:
        for e in errors:
            logger.error(f"❌ {e}")
        sys.exit(1)


def start_webhook_thread():
    """Flask webhook server ko background thread mein chalaao."""
    from webhook_server import app
    from config import WEBHOOK_HOST, WEBHOOK_PORT

    def run():
        logger.info(f"✅ Webhook server → http://{WEBHOOK_HOST}:{WEBHOOK_PORT}")
        app.run(host=WEBHOOK_HOST, port=WEBHOOK_PORT,
                debug=False, use_reloader=False)

    t = threading.Thread(target=run, daemon=True, name="WebhookServer")
    t.start()
    time.sleep(1.5)   # server ke ready hone ka wait
    return t


def main():
    print(BANNER)
    check_config()

    logger.info("Starting system...")
    start_webhook_thread()

    # Telegram bot main thread mein chalaao (blocking)
    from bot_control import run_bot
    logger.info("✅ Telegram bot starting...")
    logger.info("💡 Telegram pe /start bhejo aur setup karo.")
    run_bot()


if __name__ == "__main__":
    main()
