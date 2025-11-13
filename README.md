# Instagram Analyzer Web Application

Instagram profillarini tahlil qilish, followerlar ma'lumotlarini olish va Excel formatida yuklab olish uchun veb-ilova.

## 🚀 Imkoniyatlar

- ✅ Instagram profil ma'lumotlarini olish
- ✅ Followerlar ro'yxatini yuklash
- ✅ Ma'lumotlarni Excel formatida yuklab olish
- ✅ Random follower tanlash (konkurs uchun)
- ✅ Top followers ko'rsatish (verified va ochiq profillar)
- ✅ Responsive dizayn (mobil qurilmalarda ishlaydi)
- ✅ O'zbek tilida interfeys

## 📋 Talablar

- Python 3.8 yoki yuqori
- RapidAPI hisobi va Instagram Social API kaliti

## 🔧 O'rnatish

### 1. Repozitoriyni klonlash yoki fayllarni yuklab olish

```bash
# Agar Git orqali bo'lsa
git clone <repository-url>
cd instagram-analyzer

# Yoki fayllarni qo'lda yuklab oling
```

### 2. Virtual muhit yaratish (ixtiyoriy, lekin tavsiya etiladi)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Kerakli kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 4. RapidAPI kalitini sozlash

#### A. Muhit o'zgaruvchisi orqali (Tavsiya etiladi):

**Windows:**
```bash
set RAPIDAPI_KEY=sizning_api_kalitingiz
```

**Linux/Mac:**
```bash
export RAPIDAPI_KEY=sizning_api_kalitingiz
```

#### B. Yoki `app.py` faylida to'g'ridan-to'g'ri:

`app.py` faylini oching va 14-qatorda o'zgartiring:

```python
API_KEY = 'sizning_api_kalitingiz'
```

## 🎯 RapidAPI Kalitini Olish

1. [RapidAPI](https://rapidapi.com/) saytiga kiring
2. Ro'yxatdan o'ting yoki tizimga kiring
3. [Instagram Social API](https://rapidapi.com/api/instagram-social-api/) sahifasiga o'ting
4. "Subscribe to Test" tugmasini bosing
5. Kerakli rejani tanlang (Free plan mavjud)
6. API kalitingizni "x-rapidapi-key" ostida toping

## 🚀 Ishga tushirish

```bash
python app.py
```

Brauzeringizda quyidagi manzilni oching:
```
http://localhost:5000
```

## 📱 Foydalanish

### 1. Profil Ma'lumotlarini Olish
- Instagram username kiriting (@ belgisisiz)
- "👤 Profil Ma'lumotlari" tugmasini bosing
- Followers, following, postlar soni ko'rsatiladi

### 2. Followerlarni Yuklash
- Username kiriting
- Maksimal followerlar sonini belgilang (10-1000)
- "👥 Followerlarni Olish" tugmasini bosing
- Ro'yxat jadval ko'rinishida ko'rsatiladi

### 3. Excel Formatida Yuklab Olish
- Followerlar yuklanganidan keyin
- "📥 Excel Yuklab Olish" tugmasini bosing
- Fayl avtomatik yuklab olinadi

### 4. Random Follower Tanlash
- "🎲 Random Tanlash" tugmasini bosing
- Tasodifiy tanlangan follower ko'rsatiladi
- Konkurslar uchun foydali

### 5. Top Followers Ko'rsatish
- "⭐ Top Followers" tugmasini bosing
- Verified va ochiq profillar birinchi o'rinda ko'rsatiladi

## 📊 Excel Fayl Tarkibi

Excel faylda quyidagi ustunlar bo'ladi:
- Username
- To'liq Ism
- ID
- Tasdiqlangan (Verified)
- Maxfiy (Private)
- Profil Havolasi

## 🔐 Xavfsizlik

- ❗ API kalitingizni hech kimga bermang
- ❗ API kalitini GitHub yoki ommaviy joylarga joylashtirmang
- ✅ Muhit o'zgaruvchisidan foydalaning
- ✅ `.env` faylini `.gitignore`ga qo'shing

## 🐛 Muammolarni Hal Qilish

### API kaliti ishlamayapti
- RapidAPI'da obuna faolligini tekshiring
- API kalitini to'g'ri nusxalashga ishonch hosil qiling
- Free plan limitiga yetmaganingizni tekshiring

### Followerlar yuklanmayapti
- Internet aloqangizni tekshiring
- Username to'g'ri kiritilganini tekshiring
- Profil ochiq (public) ekanligini tekshiring

### Excel yuklab olinmayapti
- Brauzer popup blocker o'chirilganini tekshiring
- Followerlar avval yuklanganini tekshiring

## 🛠️ Texnologiyalar

**Backend:**
- Flask - Python web framework
- aiohttp - Async HTTP so'rovlar
- pandas - Ma'lumotlar tahlili
- openpyxl - Excel fayllari bilan ishlash

**Frontend:**
- HTML5
- CSS3 (Gradient dizayn)
- Vanilla JavaScript
- Responsive dizayn

## 📝 Fayl Tuzilishi

```
instagram-analyzer/
│
├── app.py                  # Flask backend
├── instagram_api.py        # Instagram API klassi
├── requirements.txt        # Python kutubxonalari
├── README.md              # Hujjatlar
│
└── templates/
    └── index.html         # Frontend interface
```

## 🤝 Hissa Qo'shish

Agar sizda takliflar yoki yaxshilashlar bo'lsa, pull request yuborishingiz mumkin!

## 📞 Yordam

Muammolar yoki savollar uchun:
- Issue ochish
- Email: your-email@example.com

## ⚖️ Litsenziya

Ushbu loyiha shaxsiy foydalanish uchun. RapidAPI shartlariga rioya qiling.

## 🙏 Minnatdorchilik

- RapidAPI - Instagram Social API uchun
- Flask - Ajoyib web framework uchun
- Barcha open-source kutubxona dasturchilarga

---

**Diqqat:** Instagram'ning Terms of Service'ga rioya qiling va API dan mas'uliyat bilan foydalaning!
