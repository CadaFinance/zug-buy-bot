import os
from dotenv import load_dotenv
import random
from datetime import datetime, timedelta
import requests
import json

load_dotenv()

# Telegram Bot Token
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Grup ID'si
GROUP_ID = os.getenv('GROUP_ID')

# Hedef tarih ve miktar  
TARGET_DATE = datetime(2025, 8, 19, 8, 30, 0)  # 19/08/2025 08:30 UTC
TARGET_AMOUNT = 1500920  # $1,500,920

# Başlangıç tarihi
START_DATE = datetime(2025, 8, 11, 8, 30, 0)  # 09/08/2025 08:30 UTC



# Bot çalışma saatleri (UTC) - 24 saat boyunca
WORK_START_HOUR = 0   # Saat 0'da başla (gece yarısı)
WORK_END_HOUR = 24    # Saat 24'te bitir (ertesi gün gece yarısı)

# Her saatte gönderilecek mesaj sayısı (5 dakika aralıklarla)
MESSAGES_PER_HOUR = 9  # Her saatte 9 mesaj

# ZUG Chain projesi
ZUG_CHAIN = {
    "name": "ZUG Chain",
    "website": "https://www.zugchain.org",
    "twitter": "https://x.com/ZugChain_org",
    "whitepaper": "https://www.zugchain.org/zugwhitepaper.pdf"
}

# Video dosyası yolu (MP4)
VIDEO_PATH = "presale.mp4"

# Global değişken - toplam miktar
current_total_amount = 0

# Toplam miktarı saklamak için dosya
TOTAL_SAVE_FILE = "total_amount.json"

def get_utc_time():
    """İnternetten gerçek UTC zamanını al"""
    try:
        # TimeAPI.io
        response = requests.get('https://timeapi.io/api/Time/current/zone?timeZone=UTC', timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Format: 2025-08-09T08:24:08.9602938
            time_str = data['dateTime'][:19]  # İlk 19 karakter: YYYY-MM-DDTHH:MM:SS
            utc_time = datetime.fromisoformat(time_str)
            print(f"✓ İnternet UTC: {utc_time.strftime('%H:%M:%S')}")
            return utc_time
    except Exception as e:
        print(f"TimeAPI hatası: {str(e)[:50]}")
    
    try:
        # JSONTest.com
        response = requests.get('https://jsontest.com/', timeout=5)
        # Bu çalışmazsa başka API dene
    except:
        pass
    
    try:
        # Manuel olarak şu anki zamanı ayarlayalım - test için
        # Gerçek UTC 08:24 civarı, 08:25'e kadar bekleyecek
        now = datetime.utcnow()
        print(f"⚠️ Yerel UTC kullanılıyor: {now.strftime('%H:%M:%S')}")
        return now
    except Exception as e:
        print(f"Hata: {e}")
        return datetime.utcnow()

def load_total_amount():
    """Kaydedilmiş toplam miktarı yükle"""
    global current_total_amount
    try:
        if os.path.exists(TOTAL_SAVE_FILE):
            with open(TOTAL_SAVE_FILE, 'r') as f:
                data = json.load(f)
                current_total_amount = data.get('total_amount', 0)
                print(f"✓ Kaydedilmiş toplam miktar yüklendi: ${current_total_amount:,.2f}")
                return current_total_amount
    except Exception as e:
        print(f"Toplam miktar yükleme hatası: {e}")
    
    return 0

def save_total_amount():
    """Toplam miktarı kaydet"""
    try:
        data = {'total_amount': current_total_amount}
        with open(TOTAL_SAVE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Toplam miktar kaydedildi: ${current_total_amount:,.2f}")
    except Exception as e:
        print(f"Toplam miktar kaydetme hatası: {e}")

def calculate_current_total():
    """Hedef tarihe kadar geçen süreye göre mevcut toplam miktarı hesapla"""
    global current_total_amount
    now = get_utc_time()
    
    # Başlangıç tarihinden önceyse 0 döndür
    if now < START_DATE:
        current_total_amount = 0
        return 0
    
    # Hedef tarihe ulaştıysa tam miktarı döndür
    if now >= TARGET_DATE:
        current_total_amount = TARGET_AMOUNT
        return TARGET_AMOUNT
    
    # Toplam süre (saniye)
    total_duration = (TARGET_DATE - START_DATE).total_seconds()
    
    # Geçen süre (saniye)
    elapsed_duration = (now - START_DATE).total_seconds()
    
    # İlerleme oranı
    progress_ratio = elapsed_duration / total_duration
    
    # Mevcut toplam miktar
    current_total_amount = TARGET_AMOUNT * progress_ratio
    
    return round(current_total_amount, 2)

def add_to_total(amount):
    """Toplam miktara ekle ve kaydet"""
    global current_total_amount
    current_total_amount += amount
    save_total_amount()  # Her eklemeden sonra kaydet
    return round(current_total_amount, 2)

def generate_hourly_schedule():
    """Saatteki 12 mesaj için gerçekçi 5+ dakika aralıklarla dakika programı oluştur"""
    minutes = []
    current_minute = 0
    
    while len(minutes) < MESSAGES_PER_HOUR:
        # 5-15 dakika arası rastgele aralık
        interval = random.randint(5, 15)
        current_minute += interval
        
        if current_minute < 60:
            minutes.append(current_minute)
        else:
            break
    
    # Eğer yeterli mesaj yoksa, kalan dakikalardan rastgele seç
    remaining_minutes = [m for m in range(60) if m not in minutes]
    while len(minutes) < MESSAGES_PER_HOUR and remaining_minutes:
        minutes.append(remaining_minutes.pop(random.randint(0, len(remaining_minutes)-1)))
    
    return sorted(minutes)

def generate_full_schedule():
    """Başlangıçtan bitişe kadar tüm mesaj zamanlarını hesapla ve sakla"""
    schedule = []
    current_date = START_DATE
    
    while current_date < TARGET_DATE:
        # Sadece çalışma saatlerinde mesaj gönder
        if WORK_START_HOUR <= current_date.hour < WORK_END_HOUR:
            # Bu saatteki mesaj programını al
            hourly_minutes = generate_hourly_schedule()
            
            for minute in hourly_minutes:
                message_time = current_date.replace(
                    minute=minute, 
                    second=0, 
                    microsecond=0
                )
                schedule.append(message_time)
        
        # Bir sonraki saate geç
        current_date += timedelta(hours=1)
    
    # Zamanları sırala
    schedule.sort()
    return schedule



def generate_presale_message():
    """ZUG Chain presale mesajı oluştur"""
    # Gerçekçi miktar dağılımı
    # %60 küçük alımlar ($50-$150)
    # %30 orta alımlar ($150-$300)
    # %10 büyük alımlar ($300-$500)
    
    rand = random.random()
    
    if rand < 0.6:  # %60 küçük alımlar
        amount = round(random.uniform(50, 150), 2)
    elif rand < 0.9:  # %30 orta alımlar
        amount = round(random.uniform(150, 300), 2)
    else:  # %10 büyük alımlar
        amount = round(random.uniform(300, 500), 2)
    
    # Gerçek UTC zamanı (saniye dahil) - rastgele saniye ekle
    current_time = get_utc_time()
    # ±30 saniye rastgele ekle
    random_seconds = random.randint(-30, 30)
    current_time = current_time + timedelta(seconds=random_seconds)
    date_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Yeni toplam miktar
    total_raise = add_to_total(amount)
    
    # Ateş emojisi hesaplama
    if amount < 80:
        # $80 altı için her $10 için 1 ateş
        fire_count = int(amount // 10)
        fire_emojis = "🔥" * fire_count
    else:
        # $80 üzeri için her $10 için 2 ateş
        fire_count = int(amount // 10) * 2
        fire_emojis = "🔥" * fire_count
    
    message = f"""{ZUG_CHAIN['name']} Presale Buy!

<b>Date (UTC time):</b> {date_str}
<b>Amount:</b> ${amount:,.2f}

<b>Total Presale Raise:</b> ${total_raise:,.2f}

{fire_emojis}

<a href="{ZUG_CHAIN['website']}">Website</a> - <a href="{ZUG_CHAIN['twitter']}">X (Twitter)</a> - <a href="{ZUG_CHAIN['whitepaper']}">Whitepaper</a>"""
    
    return message, amount
