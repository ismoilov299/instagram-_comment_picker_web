@echo off
echo 🚀 Instagram Analyzer ishga tushirilmoqda...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Virtual muhit yaratilmoqda...
    python -m venv venv
)

REM Activate virtual environment
echo ✅ Virtual muhit faollashtirilmoqda...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Kutubxonalar o'rnatilmoqda...
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo.
    echo ⚠️  .env fayli topilmadi!
    echo 📝 .env.example faylidan nusxa oling va API kalitingizni kiriting:
    echo    copy .env.example .env
    echo    notepad .env
    echo.
)

REM Run the app
echo.
echo 🌐 Server ishga tushmoqda...
echo 📱 Brauzeringizda http://localhost:5000 ni oching
echo.
python app.py

pause
