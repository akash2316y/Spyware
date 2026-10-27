#!/bin/bash
# ───────────────────────────────────────────────────────
#  setup.sh  —  Linux / macOS setup script
# ───────────────────────────────────────────────────────
set -e

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   Instagram Telegram Monitor Setup   ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── Python version check ──────────────────────
PYTHON=$(command -v python3 || command -v python)
if [ -z "$PYTHON" ]; then
    echo "❌ Python nahi mila. Python 3.9+ install karo."
    exit 1
fi

PY_VER=$($PYTHON -c "import sys; print(sys.version_info.minor)")
echo "✅ Python found: $($PYTHON --version)"

# ── Virtual environment ───────────────────────
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment bana raha hoon..."
    $PYTHON -m venv venv
fi

source venv/bin/activate
echo "✅ venv activated"

# ── Install dependencies ──────────────────────
echo "📥 Dependencies install ho rahi hain..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ Dependencies installed"

# ── .env file ─────────────────────────────────
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  .env file bani hai — isko ZAROOR edit karo:"
    echo "    nano .env"
    echo ""
else
    echo "✅ .env already exists"
fi

echo ""
echo "═══════════════════════════════════════"
echo "  Next Steps (README.md padho):"
echo ""
echo "  1. nano .env          # config bharo"
echo "  2. Instagram session:"
echo "     instagram_monitor --login YOUR_IG_USERNAME"
echo "  3. python run.py      # system start karo"
echo "═══════════════════════════════════════"
echo ""
