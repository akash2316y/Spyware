"""
webhook_server.py
-----------------
Flask server jo instagram_monitor se webhook receive karta hai
aur Telegram channel pe media + message bhejta hai.
"""

import os
import json
import logging
import tempfile
from datetime import datetime

import requests as req
from flask import Flask, request, jsonify

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHANNEL_ID,
    WEBHOOK_HOST,
    WEBHOOK_PORT,
)

app = Flask(__name__)
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [WEBHOOK] %(message)s")
logger = logging.getLogger(__name__)

# ── Helper: timestamp ─────────────────────────────────────

def timestamp() -> str:
    return datetime.now().strftime("📅 %d/%m/%Y   🕐 %H:%M:%S")


# ── Telegram senders ──────────────────────────────────────

def tg_url(method: str) -> str:
    return f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"


def send_text(chat_id: str, text: str):
    try:
        req.post(tg_url("sendMessage"),
                 json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
                 timeout=15)
    except Exception as e:
        logger.error(f"send_text failed: {e}")


def send_photo(chat_id: str, path: str, caption: str):
    try:
        with open(path, "rb") as f:
            req.post(tg_url("sendPhoto"),
                     data={"chat_id": chat_id, "caption": caption,
                           "parse_mode": "Markdown"},
                     files={"photo": f}, timeout=60)
    except Exception as e:
        logger.error(f"send_photo failed: {e}")
        send_text(chat_id, caption + "\n\n_(Photo send failed)_")


def send_video(chat_id: str, path: str, caption: str):
    try:
        with open(path, "rb") as f:
            req.post(tg_url("sendVideo"),
                     data={"chat_id": chat_id, "caption": caption,
                           "parse_mode": "Markdown"},
                     files={"video": f}, timeout=120)
    except Exception as e:
        logger.error(f"send_video failed: {e}")
        send_text(chat_id, caption + "\n\n_(Video send failed)_")


def send_document(chat_id: str, path: str, caption: str):
    try:
        with open(path, "rb") as f:
            req.post(tg_url("sendDocument"),
                     data={"chat_id": chat_id, "caption": caption,
                           "parse_mode": "Markdown"},
                     files={"document": f}, timeout=120)
    except Exception as e:
        logger.error(f"send_document failed: {e}")
        send_text(chat_id, caption + "\n\n_(Document send failed)_")


# ── Media router ──────────────────────────────────────────

VIDEO_EXTS  = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
IMAGE_EXTS  = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

def download_url(url: str, suffix: str = ".jpg") -> str | None:
    """URL se file download karke temp path return karo."""
    try:
        r = req.get(url, timeout=60, stream=True)
        r.raise_for_status()
        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        for chunk in r.iter_content(chunk_size=8192):
            tmp.write(chunk)
        tmp.close()
        logger.info(f"Downloaded to {tmp.name}")
        return tmp.name
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return None


def route_media(chat_id: str, path: str, caption: str, is_temp: bool = False):
    """File type dekh ke sahi Telegram method use karo."""
    if not os.path.exists(path):
        send_text(chat_id, caption + "\n\n_(Media file missing)_")
        return

    ext       = os.path.splitext(path)[1].lower()
    file_size = os.path.getsize(path)

    if ext in VIDEO_EXTS:
        if file_size < 50 * 1024 * 1024:   # < 50 MB → sendVideo
            send_video(chat_id, path, caption)
        else:
            send_document(chat_id, path, caption)
    elif ext in IMAGE_EXTS:
        if file_size < 10 * 1024 * 1024:   # < 10 MB → sendPhoto
            send_photo(chat_id, path, caption)
        else:
            send_document(chat_id, path, caption)
    else:
        send_document(chat_id, path, caption)

    if is_temp:
        try:
            os.unlink(path)
        except Exception:
            pass


# ── Event emoji map ───────────────────────────────────────

EMOJI = {
    "new_post"    : "📸",
    "new_reel"    : "🎬",
    "new_story"   : "📖",
    "story"       : "📖",
    "post"        : "📸",
    "reel"        : "🎬",
    "bio"         : "✏️",
    "profile_pic" : "🖼️",
    "follower"    : "👥",
    "following"   : "🔗",
    "visibility"  : "🔒",
    "error"       : "❌",
    "login"       : "🔑",
}

def get_emoji(event_type: str) -> str:
    et = event_type.lower()
    for key, val in EMOJI.items():
        if key in et:
            return val
    return "🔔"


# ── Webhook endpoint ──────────────────────────────────────

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.json or {}
        logger.info(f"Received: {json.dumps(data)[:300]}")

        # Fields extract karo (instagram_monitor ka flexible format handle karo)
        event_type  = data.get("event_type") or data.get("type") or "update"
        username    = data.get("username")   or data.get("user")  or "unknown"
        message     = data.get("message")    or data.get("text")  or str(data)
        media_url   = data.get("media_url")  or data.get("url")   or ""
        local_file  = data.get("local_file") or data.get("file_path") or ""
        extra_info  = data.get("extra", "")

        emoji = get_emoji(event_type)

        caption = (
            f"{emoji} *Instagram Alert*\n"
            f"👤 User: `{username}`\n"
            f"{timestamp()}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📌 Event: `{event_type}`\n"
            f"{message}"
        )
        if extra_info:
            caption += f"\n\n_{extra_info}_"

        # Media bhejo — local file > URL > sirf text
        if local_file and os.path.exists(local_file):
            route_media(TELEGRAM_CHANNEL_ID, local_file, caption, is_temp=False)

        elif media_url:
            # Extension guess karo
            if any(ext in media_url.lower() for ext in ["mp4", "reel", "video"]):
                suffix = ".mp4"
            else:
                suffix = ".jpg"
            tmp_path = download_url(media_url, suffix)
            if tmp_path:
                route_media(TELEGRAM_CHANNEL_ID, tmp_path, caption, is_temp=True)
            else:
                send_text(TELEGRAM_CHANNEL_ID, caption)

        else:
            send_text(TELEGRAM_CHANNEL_ID, caption)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        logger.error(f"Webhook error: {e}", exc_info=True)
        return jsonify({"status": "error", "detail": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running",
                    "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}), 200


if __name__ == "__main__":
    logger.info(f"Webhook server starting on {WEBHOOK_HOST}:{WEBHOOK_PORT}")
    app.run(host=WEBHOOK_HOST, port=WEBHOOK_PORT,
            debug=False, use_reloader=False)
