@echo off
REM ──────────────────────────────────────────────────────
REM  setup.bat  —  Windows setup script
REM ──────────────────────────────────────────────────────

echo.
echo  =============================================
echo   Instagram Telegram Monitor - Windows Setup
echo  =============================================
echo.

REM ── Python check ──────────────────────────────
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo [ERROR] Python nahi mila. python.org se install karo.
    pause
    exit /b 1
)
echo [OK] Python found.

REM ── Virtual environment ───────────────────────
IF NOT EXIST "venv" (
    echo [..] venv bana raha hoon...
    python -m venv venv
)
call venv\Scripts\activate.bat
echo [OK] venv activated.

REM ── Install dependencies ──────────────────────
echo [..] Dependencies install ho rahi hain...
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo [OK] Dependencies installed.

REM ── .env file ─────────────────────────────────
IF NOT EXIST ".env" (
    copy .env.example .env
    echo.
    echo [!!] .env file bani hai - ZAROOR edit karo!
    echo      Notepad mein kholne ke liye:  notepad .env
    echo.
) ELSE (
    echo [OK] .env already exists.
)

echo.
echo  ============================================
echo   Next Steps:
echo.
echo   1. notepad .env          (config bharo)
echo   2. Instagram login:
echo      instagram_monitor --login YOUR_IG_USER
echo   3. python run.py         (system start karo)
echo  ============================================
echo.
pause
