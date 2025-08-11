import asyncio
import random
import logging
from telegram import Bot
from telegram.error import TelegramError
from telegram.constants import ParseMode
from config import (
    BOT_TOKEN, GROUP_ID, MESSAGES_PER_HOUR, VIDEO_PATH,
    generate_presale_message, calculate_current_total, generate_hourly_schedule,
    generate_full_schedule, get_utc_time, WORK_START_HOUR, WORK_END_HOUR,
    load_total_amount
)
from datetime import datetime, timedelta
import os
import json
from aiohttp import web
import threading

# Logging ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class PresaleBot:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.running = False
        self.full_schedule = []
        self.current_message_index = 0
        self.sent_messages = 0
        self.http_server = None
        self.http_thread = None
        
    async def send_presale_message(self):
        """Presale mesajı video ile gönder ve pinle"""
        try:
            message, amount = generate_presale_message()
            
            # Video dosyası varsa video ile gönder, yoksa sadece metin
            if os.path.exists(VIDEO_PATH):
                with open(VIDEO_PATH, 'rb') as video_file:
                    sent_message = await self.bot.send_animation(
                        chat_id=GROUP_ID,
                        animation=video_file,
                        caption=message,
                        parse_mode=ParseMode.HTML
                    )
            else:
                # Video yoksa sadece metin gönder
                sent_message = await self.bot.send_message(
                    chat_id=GROUP_ID,
                    text=message,
                    parse_mode=ParseMode.HTML
                )
            

            
            self.sent_messages += 1
            logger.info(f"Presale mesajı gönderildi - Saat: {get_utc_time().strftime('%H:%M')} - Miktar: ${amount:,.2f}")
            
        except TelegramError as e:
            logger.error(f"Mesaj gönderme hatası: {e}")
    
    async def get_total_amount(self, request):
        """Total amount endpoint"""
        try:
            if os.path.exists("total_amount.json"):
                with open("total_amount.json", 'r') as f:
                    data = json.load(f)
                    total_amount = data.get('total_amount', 0)
                    
                    return web.json_response({
                        "success": True,
                        "total_amount": total_amount,
                        "total_amount_formatted": f"${total_amount:,.2f}",
                        "currency": "USD",
                        "timestamp": datetime.utcnow().isoformat(),
                        "project": "ZUG Chain"
                    })
            else:
                return web.json_response({
                    "success": False,
                    "error": "Total amount file not found",
                    "total_amount": 0
                }, status=404)
                
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e),
                "total_amount": 0
            }, status=500)
    
    async def get_status(self, request):
        """Status endpoint"""
        try:
            total_amount = 0
            if os.path.exists("total_amount.json"):
                with open("total_amount.json", 'r') as f:
                    data = json.load(f)
                    total_amount = data.get('total_amount', 0)
            
            return web.json_response({
                "success": True,
                "status": "running",
                "total_amount": total_amount,
                "total_amount_formatted": f"${total_amount:,.2f}",
                "last_updated": datetime.utcnow().isoformat(),
                "project": "ZUG Chain"
            })
            
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)
    
    async def start_http_server(self):
        """HTTP server'ı başlat"""
        app = web.Application()
        app.router.add_get('/api/total', self.get_total_amount)
        app.router.add_get('/api/status', self.get_status)
        
        runner = web.AppRunner(app)
        self.http_server = runner
        
        await runner.setup()
        
        # Railway'de PORT environment variable'ını kullan
        port = int(os.environ.get('PORT', 5000))
        host = '0.0.0.0'  # Railway için 0.0.0.0 kullan
        
        site = web.TCPSite(runner, host, port)
        await site.start()
        logger.info(f"🌐 HTTP Server başlatıldı: http://{host}:{port}")
        logger.info("📊 Endpoints:")
        logger.info("   - GET /api/total     - Toplam miktar")
        logger.info("   - GET /api/status   - Bot durumu")

    def get_next_message_time(self):
        """Bir sonraki mesaj zamanını hesapla"""
        now = get_utc_time()
        current_hour = now.hour
        
        # Sadece çalışma saatlerinde mesaj gönder (4-13 arası)
        if not (WORK_START_HOUR <= current_hour < WORK_END_HOUR):
            # Çalışma saatleri dışındaysa, bir sonraki çalışma saatini bekle
            if current_hour < WORK_START_HOUR:
                # Gece yarısından sonra, sabah 4'ü bekle
                next_time = now.replace(hour=WORK_START_HOUR, minute=0, second=0, microsecond=0)
            else:
                # Öğleden sonra, ertesi gün sabah 4'ü bekle
                next_time = (now + timedelta(days=1)).replace(hour=WORK_START_HOUR, minute=0, second=0, microsecond=0)
            return next_time
        
        # Yeni saat başladıysa programı yenile
        if not hasattr(self, 'current_hour') or self.current_hour != current_hour:
            self.current_hour = current_hour
            self.hourly_schedule = generate_hourly_schedule()
            self.sent_messages = 0
            logger.info(f"Yeni saat programı oluşturuldu: {self.hourly_schedule}")
        
        # Bu saatte gönderilecek mesaj kaldı mı?
        if self.sent_messages >= MESSAGES_PER_HOUR:
            # Bir sonraki saatin başlangıcını bekle
            next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            return next_hour
        
        # Bu saatteki bir sonraki mesaj zamanı
        next_minute = self.hourly_schedule[self.sent_messages]
        next_time = now.replace(minute=next_minute, second=0, microsecond=0)
        
        # Eğer bu zaman geçmişse, hemen gönder
        if next_time <= now:
            return now
        
        return next_time
    
    async def run_bot(self):
        """Bot'u çalıştır - saatte 14 mesaj gönder"""
        self.running = True
        logger.info("Presale bot başlatıldı...")
        
        # HTTP server'ı başlat
        await self.start_http_server()
        
        # Kaydedilmiş toplam miktarı yükle
        load_total_amount()
        
        # İlk hesaplama yapma - sadece kaydedilmiş değeri kullan
        # calculate_current_total()  # Bu satırı kaldırdık
        
        while self.running:
            try:
                # Bir sonraki mesaj zamanını hesapla
                next_time = self.get_next_message_time()
                now = get_utc_time()
                
                # Bekleme süresi hesapla
                if next_time > now:
                    wait_seconds = (next_time - now).total_seconds()
                    logger.info(f"Sonraki mesaj {wait_seconds:.0f} saniye sonra gönderilecek")
                    await asyncio.sleep(wait_seconds)
                
                # Mesajı gönder
                await self.send_presale_message()
                
            except KeyboardInterrupt:
                logger.info("Bot durduruldu")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Beklenmeyen hata: {e}")
                await asyncio.sleep(10)  # Hata durumunda 10 saniye bekle
    
    def stop_bot(self):
        """Bot'u durdur"""
        self.running = False
        logger.info("Bot durdurma sinyali gönderildi")

async def main():
    """Ana fonksiyon"""
    if not BOT_TOKEN:
        print("HATA: BOT_TOKEN bulunamadı! .env dosyasını kontrol edin.")
        return
    
    if not GROUP_ID:
        print("HATA: GROUP_ID bulunamadı! .env dosyasını kontrol edin.")
        return
    
    bot = PresaleBot()
    
    try:
        await bot.run_bot()
    except KeyboardInterrupt:
        bot.stop_bot()

if __name__ == "__main__":
    asyncio.run(main())
