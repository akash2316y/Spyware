"""
bot_control.py
--------------
Telegram bot — /login, /monitor, /stop, /status commands.
Authenticated users hi monitor start/stop kar sakte hain.
"""

import asyncio
import logging
import os
import signal
import subprocess
from datetime import datetime

from telegram import Update
from telegram.ext import (Application, CommandHandler,
                           ContextTypes, MessageHandler, filters)

from config import (
    TELEGRAM_BOT_TOKEN,
    ADMIN_CHAT_ID,
    BOT_PASSWORD,
    INSTAGRAM_USERNAME,
    CHECK_INTERVAL,
    WEBHOOK_PORT,
)

logger = logging.getLogger(__name__)

# ── State ─────────────────────────────────────────────────
authenticated_users: set[str] = set()
monitor_process: subprocess.Popen | None = None
monitor_target: str = ""
monitor_start_time: datetime | None = None


def is_auth(user_id) -> bool:
    uid = str(user_id)
    return uid in authenticated_users or uid == str(ADMIN_CHAT_ID)


# ── Commands ──────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 *Instagram Monitor Bot*\n\n"
        "Pehle `/login <password>` karo, phir commands use karo:\n\n"
        "🔑 `/login pass` — Authenticate\n"
        "▶️ `/monitor username` — Monitoring shuru karo\n"
        "⏹️ `/stop` — Monitoring band karo\n"
        "📊 `/status` — Current status dekho\n"
        "🔄 `/restart` — Monitor restart karo\n"
        "ℹ️ `/help` — Full help\n",
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 *Help / Commands*\n\n"
        "*Setup steps:*\n"
        "1. `/login yourpassword`\n"
        "2. `/monitor instagram_username`\n"
        "3. Har 10 min mein updates aayenge channel pe\n\n"
        "*Control:*\n"
        "• `/stop` — monitoring rok do\n"
        "• `/status` — status check karo\n"
        "• `/restart username` — restart karo\n\n"
        "*Note:* Instagram login session pehle se set hona chahiye.\n"
        "Dekho README.md ka Step 3.",
        parse_mode="Markdown",
    )


async def cmd_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    if not context.args:
        await update.message.reply_text(
            "Usage: `/login yourpassword`", parse_mode="Markdown"
        )
        return

    if context.args[0] == BOT_PASSWORD:
        authenticated_users.add(uid)
        await update.message.reply_text(
            f"✅ *Login successful!*\n"
            f"👤 User ID: `{uid}`\n"
            f"Ab tum monitor commands use kar sakte ho.",
            parse_mode="Markdown",
        )
        logger.info(f"User {uid} authenticated.")
    else:
        await update.message.reply_text("❌ *Wrong password!*", parse_mode="Markdown")
        logger.warning(f"Failed login attempt from {uid}")


async def cmd_monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global monitor_process, monitor_target, monitor_start_time

    if not is_auth(update.effective_user.id):
        await update.message.reply_text("❌ Pehle `/login` karo.", parse_mode="Markdown")
        return

    if not context.args:
        await update.message.reply_text(
            "Usage: `/monitor instagram_username`", parse_mode="Markdown"
        )
        return

    target = context.args[0].strip().lstrip("@")

    # Pehle se chal raha hai?
    if monitor_process and monitor_process.poll() is None:
        await update.message.reply_text(
            f"⚠️ Already monitoring `{monitor_target}`.\n"
            f"Pehle `/stop` karo.",
            parse_mode="Markdown",
        )
        return

    await update.message.reply_text(
        f"⏳ Starting monitor for `{target}`...", parse_mode="Markdown"
    )

    try:
        cmd = build_monitor_cmd(target)
        monitor_process   = subprocess.Popen(
            cmd,
            stdout=open(f"monitor_{target}.log", "a"),
            stderr=subprocess.STDOUT,
        )
        monitor_target    = target
        monitor_start_time = datetime.now()

        await update.message.reply_text(
            f"✅ *Monitoring Started!*\n\n"
            f"👤 Target : `{target}`\n"
            f"⏱ Interval: Every *{CHECK_INTERVAL // 60} minutes*\n"
            f"🆔 PID     : `{monitor_process.pid}`\n"
            f"📅 Started : {monitor_start_time.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            f"Updates `#{target}` Telegram channel pe aayenge 📡",
            parse_mode="Markdown",
        )
        logger.info(f"Monitor started for {target} (PID {monitor_process.pid})")

    except FileNotFoundError:
        await update.message.reply_text(
            "❌ `instagram_monitor` command nahi mila!\n"
            "Run karo: `pip install instagram_monitor`",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: `{e}`", parse_mode="Markdown")
        logger.error(f"Start failed: {e}", exc_info=True)


async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global monitor_process, monitor_target, monitor_start_time

    if not is_auth(update.effective_user.id):
        await update.message.reply_text("❌ Pehle `/login` karo.", parse_mode="Markdown")
        return

    if not monitor_process or monitor_process.poll() is not None:
        await update.message.reply_text("⚠️ Koi monitor nahi chal raha.", parse_mode="Markdown")
        return

    saved_target = monitor_target
    try:
        monitor_process.terminate()
        monitor_process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        monitor_process.kill()

    await update.message.reply_text(
        f"🛑 *Monitor Stopped*\n👤 `{saved_target}` ki monitoring band ho gayi.",
        parse_mode="Markdown",
    )
    logger.info(f"Monitor stopped for {saved_target}")
    monitor_target    = ""
    monitor_start_time = None


async def cmd_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global monitor_process, monitor_target, monitor_start_time

    if not is_auth(update.effective_user.id):
        await update.message.reply_text("❌ Pehle `/login` karo.", parse_mode="Markdown")
        return

    # Target: argument se ya purana wala
    target = context.args[0].strip().lstrip("@") if context.args else monitor_target
    if not target:
        await update.message.reply_text(
            "Usage: `/restart username`", parse_mode="Markdown"
        )
        return

    # Stop karo agar chal raha hai
    if monitor_process and monitor_process.poll() is None:
        monitor_process.terminate()
        try:
            monitor_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            monitor_process.kill()
        await update.message.reply_text(f"⏹️ Old monitor stopped.", parse_mode="Markdown")

    # Naya shuru karo
    context.args = [target]
    await cmd_monitor(update, context)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_auth(update.effective_user.id):
        await update.message.reply_text("❌ Pehle `/login` karo.", parse_mode="Markdown")
        return

    now = datetime.now()

    if monitor_process and monitor_process.poll() is None:
        uptime = str(now - monitor_start_time).split(".")[0] if monitor_start_time else "?"
        msg = (
            f"🟢 *Monitor Running*\n\n"
            f"👤 Target  : `{monitor_target}`\n"
            f"🆔 PID     : `{monitor_process.pid}`\n"
            f"⏱ Interval: Every `{CHECK_INTERVAL // 60}` minutes\n"
            f"⏳ Uptime  : `{uptime}`\n"
            f"📅 Now     : `{now.strftime('%d/%m/%Y %H:%M:%S')}`"
        )
    else:
        msg = (
            f"🔴 *Monitor Not Running*\n\n"
            f"📅 Time: `{now.strftime('%d/%m/%Y %H:%M:%S')}`\n"
            f"Use `/monitor username` to start."
        )

    await update.message.reply_text(msg, parse_mode="Markdown")


async def cmd_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Unknown command. `/help` dekho.", parse_mode="Markdown"
    )


# ── Build command ─────────────────────────────────────────

def build_monitor_cmd(target: str) -> list[str]:
    """instagram_monitor command build karo."""
    cmd = [
        "instagram_monitor",
        target,
        "--verbose",
    ]

    # Instagram account set hai toh add karo
    if INSTAGRAM_USERNAME:
        cmd += ["--login", INSTAGRAM_USERNAME]

    # Webhook URL add karo
    cmd += ["--webhook-url", f"http://localhost:{WEBHOOK_PORT}/webhook"]

    # Check interval (agar tool support karta hai)
    cmd += ["--check-interval", str(CHECK_INTERVAL)]

    return cmd


# ── Bot runner ────────────────────────────────────────────

def run_bot():
    """Bot ko naye event loop mein chalaao (thread-safe)."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start",   cmd_start))
    application.add_handler(CommandHandler("help",    cmd_help))
    application.add_handler(CommandHandler("login",   cmd_login))
    application.add_handler(CommandHandler("monitor", cmd_monitor))
    application.add_handler(CommandHandler("stop",    cmd_stop))
    application.add_handler(CommandHandler("restart", cmd_restart))
    application.add_handler(CommandHandler("status",  cmd_status))
    application.add_handler(
        MessageHandler(filters.COMMAND, cmd_unknown)
    )

    logger.info("Telegram bot polling started.")
    application.run_polling(drop_pending_updates=True)
