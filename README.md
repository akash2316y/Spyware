# 📸 Instagram → Telegram Monitor

Har 10 minute mein Instagram private user ki activities check karo
aur sab kuch **Telegram channel** pe date/time ke saath save karo.

Videos aur photos **directly** bheje jaate hain — koi link nahi.

---

## 🏗️ System kaise kaam karta hai

```
Instagram (Private User)
        ↓  (har 10 min check)
instagram_monitor (Python)
        ↓  (webhook JSON)
webhook_server.py (Flask, port 5000)
        ↓  (media download + format)
Telegram Channel  ← date/time ke saath
        ↑
Telegram Bot  ← tum /login /monitor /stop commands dete ho
```

---

## 📋 Requirements

- Python 3.9 ya usse zyada
- Instagram account jo target user ko **follow karta ho**
- Telegram Bot Token (BotFather se)
- Telegram Channel (bot admin ho)

---

## 🚀 Step-by-Step Setup

### Step 1 — Files download karo

```bash
# Zip extract karo ya git clone karo
cd instagram_telegram_monitor
```

---

### Step 2 — Setup run karo

**Linux / macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```
setup.bat pe double-click karo
```

Yeh automatically virtual environment banata hai aur sab install karta hai.

---

### Step 3 — Instagram Session banana (ZAROOR karo)

Pehle ek baar Instagram mein login karo taaki session save ho:

```bash
# venv active karo
source venv/bin/activate        # Linux/Mac
# ya
venv\Scripts\activate.bat       # Windows

# Instagram login (sirf ek baar karna hai)
instagram_monitor --login YOUR_INSTAGRAM_USERNAME
```

Yeh ek session file save kar leta hai.
Password baar baar nahi dena padega.

---

### Step 4 — .env file bharo

```bash
nano .env          # Linux/Mac
notepad .env       # Windows
```

**Sab fields bharo:**

| Field | Kya likhna hai |
|---|---|
| `TELEGRAM_BOT_TOKEN` | BotFather se token |
| `TELEGRAM_CHANNEL_ID` | `@mychannel` ya `-100xxxxxxx` |
| `ADMIN_CHAT_ID` | [userinfobot](https://t.me/userinfobot) se ID lo |
| `BOT_PASSWORD` | Koi bhi strong password rakho |
| `INSTAGRAM_USERNAME` | Tumhara Instagram username |
| `TARGET_USERNAME` | Jis user ko monitor karna hai |
| `CHECK_INTERVAL` | `600` = 10 minutes |

---

### Step 5 — Telegram Bot setup

1. **BotFather pe jao** → `/newbot` → name aur username do
2. Token copy karo → `.env` mein `TELEGRAM_BOT_TOKEN` mein paste karo
3. **Channel banao** (ya existing use karo)
4. Bot ko channel mein **Admin** banao (post karne ki permission do)
5. [userinfobot](https://t.me/userinfobot) pe `/start` karo → apna ID lo

---

### Step 6 — System Start karo

```bash
source venv/bin/activate   # Linux/Mac
python run.py
```

**Windows:**
```
venv\Scripts\activate.bat
python run.py
```

---

### Step 7 — Telegram Bot se control karo

Apne Telegram mein bot ko message karo:

```
/start                          → welcome message
/login MySecurePass@2024        → authenticate karo
/monitor target_username        → monitoring shuru karo
/status                         → check karo sab theek hai
/stop                           → monitoring band karo
/restart target_username        → restart karo
```

---

## 📬 Telegram Channel pe kya aayega?

Jab bhi koi change hoga:

```
📸 Instagram Alert
👤 User: target_username
📅 28/05/2026   🕐 14:35:22
━━━━━━━━━━━━━━━━━━━
📌 Event: new_post
New post detected: "Caption text here"
[Photo attached directly]
```

Event types aur unke emojis:
- 📸 New Post
- 🎬 New Reel  
- 📖 New Story
- ✏️ Bio Change
- 🖼️ Profile Pic Change
- 👥 Follower Change
- 🔒 Visibility Change

---

## 🔄 Background mein chalana (Server pe)

**Linux — screen use karo:**
```bash
screen -S instamonitor
source venv/bin/activate
python run.py
# Ctrl+A then D to detach
```

**Linux — systemd service:**
```ini
# /etc/systemd/system/instamonitor.service
[Unit]
Description=Instagram Monitor

[Service]
WorkingDirectory=/path/to/instagram_telegram_monitor
ExecStart=/path/to/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable instamonitor
sudo systemctl start instamonitor
```

---

## ❓ Troubleshooting

**Bot respond nahi kar raha:**
- Token sahi hai?
- Bot channel mein admin hai?
- `/login password` kiya?

**Instagram data nahi aa raha:**
- Session sahi se bana? Step 3 dobara karo
- Target user ko follow karte ho?
- Instagram ne account block toh nahi kiya?

**Media nahi aa rahi:**
- File size check karo (50MB+ videos Telegram accept nahi karta)
- Video documents ke roop mein aayengi agar size zyada ho

**Port already in use error:**
- `.env` mein `WEBHOOK_PORT=5001` kar do

---

## 📁 File Structure

```
instagram_telegram_monitor/
├── .env.example        ← config template
├── .env                ← tumhari actual config (git mein nahi jaata)
├── config.py           ← env vars loader
├── webhook_server.py   ← Flask server (instagram → telegram)
├── bot_control.py      ← Telegram bot commands
├── run.py              ← main entry point
├── requirements.txt    ← Python dependencies
├── setup.sh            ← Linux/Mac setup
├── setup.bat           ← Windows setup
└── README.md           ← yeh file
```

---

## ⚠️ Legal / Ethical Notice

Yeh tool sirf **apni khud ki account** ya **consented user** ke liye use karo.
Kisi ko bina unki permission ke track karna illegal ho sakta hai.
instagram_monitor **GPLv3** license ke under hai.

---

*Questions? README dobara padho ya GitHub Issues check karo.*
