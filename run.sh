#!/bin/bash

echo "🚀 Instagram Analyzer ishga tushirilmoqda..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual muhit yaratilmoqda..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✅ Virtual muhit faollashtirilmoqda..."
source venv/bin/activate

# Install requirements
echo "📥 Kutubxonalar o'rnatilmoqda..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env fayli topilmadi!"
    echo "📝 .env.example faylidan nusxa oling va API kalitingizni kiriting:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    echo ""
fi

# Run the app
echo ""
echo "🌐 Server ishga tushmoqda..."
echo "📱 Brauzeringizda http://localhost:5000 ni oching"
echo ""
python app.py
