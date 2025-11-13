"""
Instagram API Test Script
Bu skript API kaliti to'g'ri ishlashini tekshirish uchun
"""
import asyncio
import sys
import os

# Instagram API ni import qilish
from instagram_api import InstagramAPI

async def test_api():
    """API ni test qilish"""
    
    # API kalitini olish
    api_key = os.getenv('RAPIDAPI_KEY', 'YOUR_RAPIDAPI_KEY_HERE')
    
    if api_key == 'YOUR_RAPIDAPI_KEY_HERE':
        print("❌ API kaliti topilmadi!")
        print("📝 .env faylini yarating yoki RAPIDAPI_KEY muhit o'zgaruvchisini belgilang")
        return False
    
    print("🔍 API test qilinmoqda...")
    print(f"🔑 API Key: {api_key[:10]}...")
    print()
    
    # API obyektini yaratish
    api = InstagramAPI(api_key=api_key)
    
    try:
        # Health check
        print("1️⃣ Health check...")
        is_healthy = await api.health_check()
        
        if is_healthy:
            print("✅ API muvaffaqiyatli ishlayapti!")
            print()
            
            # API ma'lumotlarini ko'rsatish
            info = api.get_api_info()
            print("📊 API Ma'lumotlari:")
            for key, value in info.items():
                print(f"   {key}: {value}")
            print()
            
            # Test foydalanuvchi ma'lumotlarini olish
            print("2️⃣ Test foydalanuvchi (@instagram) ma'lumotlarini olish...")
            user_info = await api.get_user_info("instagram")
            
            if user_info:
                print("✅ Foydalanuvchi ma'lumotlari olindi!")
                print(f"   Username: @{user_info['username']}")
                print(f"   Followers: {user_info['followers_count']:,}")
                print(f"   Following: {user_info['following_count']:,}")
                print(f"   Postlar: {user_info['posts_count']:,}")
                print()
                
                print("🎉 Barcha testlar muvaffaqiyatli o'tdi!")
                print("✨ Siz web dasturni ishlatishingiz mumkin!")
                return True
            else:
                print("❌ Foydalanuvchi ma'lumotlarini olishda xatolik")
                return False
        else:
            print("❌ API javob bermayapti!")
            print("🔧 Quyidagilarni tekshiring:")
            print("   1. API kaliti to'g'ri")
            print("   2. RapidAPI obunangiz faol")
            print("   3. Internet aloqangiz ishlayapti")
            return False
            
    except Exception as e:
        print(f"❌ Xatolik: {str(e)}")
        return False
    finally:
        await api.close()

def main():
    """Asosiy funksiya"""
    print("=" * 60)
    print("Instagram API Test")
    print("=" * 60)
    print()
    
    # Test ni ishga tushirish
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(test_api())
    
    print()
    print("=" * 60)
    
    if success:
        print("✅ TEST MUVAFFAQIYATLI")
        print("🚀 Endi 'python app.py' bilan web dasturni ishga tushiring")
    else:
        print("❌ TEST MUVAFFAQIYATSIZ")
        print("📖 README.md faylini o'qing")
    
    print("=" * 60)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
