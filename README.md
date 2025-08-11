# Bitcoin HYPER Presale Bot

Telegram gruplarına gerçek zamanlı UTC tarihle ve hedef miktara göre Bitcoin HYPER presale buy mesajları gönderen bot.

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. `.env` dosyası oluşturun:
```bash
echo "BOT_TOKEN=your_bot_token_here" > .env
echo "GROUP_ID=your_group_id_here" >> .env
```

3. `.env` dosyasını düzenleyin:
- `BOT_TOKEN`: BotFather'dan aldığınız bot token
- `GROUP_ID`: Mesaj göndermek istediğiniz grup ID'si

4. (Opsiyonel) Video ekleyin:
- `presale.mp4` dosyasını proje klasörüne ekleyin
- Bot otomatik olarak video'yu mesajla birlikte gönderecek

## Kullanım

Bot'u çalıştırmak için:
```bash
python bot.py
```

## Özellikler

- **Gerçek zamanlı UTC tarih**: İnternetten alınan güncel UTC zamanı
- **Hedef miktar**: 14/08/2025 12:00 UTC'ye kadar $1,500,920'ye ulaşacak şekilde hesaplanır
- **Saatte 14 mesaj**: Her saatte 14 farklı dakikada mesaj gönderir
- **Rastgele program**: Her saat farklı dakikalarda mesaj gönderir (doğal görünüm)
- **Bitcoin HYPER odaklı**: Sadece Bitcoin HYPER presale mesajları
- **Gerçekçi miktarlar**: $50-$500 arası rastgele alım miktarları
- **Video desteği**: Mesajların üstünde MP4 video gösterir
- **Hata durumunda otomatik yeniden başlatma**
- **Detaylı logging**

## Mesaj Formatı

Bot şu formatta mesajlar gönderir:
```
[Video]

Bitcoin HYPER Presale Buy!

Date (UTC time): 2025-08-05 14:30:45
Amount: $137.77

Total Presale Raise: $461,820.00

🔥🔥🔥

Website - X (Twitter) - Whitepaper
```

**Ateş Emojisi Kuralları:**
- **$50-$80**: Her $10 için 1 ateş
- **$80+**: Her $10 için 2 ateş
- **Örnek**: $75 = 7 ateş, $150 = 30 ateş, $300 = 60 ateş

## Video Ekleme

1. `presale.mp4` dosyasını proje klasörüne ekleyin
2. Bot otomatik olarak video'yu mesajla birlikte gönderecek
3. Video yoksa sadece metin gönderir

## Video Özellikleri

**Önerilen MP4 Özellikleri:**
- **Boyut**: 10-20 MB
- **Çözünürlük**: 1280x720 veya 1920x1080
- **Süre**: 5-10 saniye
- **Format**: MP4 (H.264 codec)
- **FPS**: 24-30

**Telegram Sınırları:**
- Maksimum dosya boyutu: 50 MB
- Önerilen boyut: 15-20 MB
- Telegram otomatik olarak MP4'ü GIF'e dönüştürür

## Çalışma Mantığı

- Her saat başında 14 farklı dakika seçilir (0-59 arası)
- Mesajlar bu dakikalarda gönderilir
- Toplam miktar, hedef tarihe göre gerçek zamanlı hesaplanır
- UTC zamanı internetten alınır
- Sadece Bitcoin HYPER projesi için mesaj gönderir
- Video varsa mesajla birlikte gönderir

## Grup ID Alma

Grup ID'sini almak için:
1. Bot'u gruba ekleyin
2. Grupta bir mesaj gönderin
3. `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates` adresini ziyaret edin
4. `chat.id` değerini kopyalayın