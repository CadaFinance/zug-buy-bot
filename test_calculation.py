from datetime import datetime
from config import calculate_current_total, TARGET_DATE, TARGET_AMOUNT, START_DATE

def test_calculation():
    """Hesaplama testi"""
    print("=== Presale Hesaplama Testi ===")
    print(f"Başlangıç: {START_DATE.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"Hedef: {TARGET_DATE.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print(f"Hedef Miktar: ${TARGET_AMOUNT:,.2f}")
    print()
    
    # Farklı tarihler için test
    test_dates = [
        datetime(2025, 7, 30, 12, 0, 0),   # Başlangıç öncesi
        datetime(2025, 8, 1, 11, 59, 0),   # Başlangıç öncesi (1 dakika)
        datetime(2025, 8, 1, 12, 0, 0),    # Başlangıç
        datetime(2025, 8, 5, 12, 0, 0),    # Başlangıç sonrası
        datetime(2025, 8, 10, 12, 0, 0),   # Hedef öncesi
        datetime(2025, 8, 14, 11, 59, 0),  # Hedef öncesi (1 dakika)
        datetime(2025, 8, 14, 12, 0, 0),   # Hedef tarih
        datetime(2025, 8, 20, 12, 0, 0),   # Hedef sonrası
    ]
    
    for test_date in test_dates:
        # Test için tarihi değiştir
        import datetime as dt
        original_utcnow = dt.datetime.utcnow
        
        def mock_utcnow():
            return test_date
        
        dt.datetime.utcnow = mock_utcnow
        
        # Hesapla
        total = calculate_current_total()
        
        print(f"{test_date.strftime('%Y-%m-%d %H:%M:%S')}: ${total:,.2f}")
        
        # Orijinal fonksiyonu geri yükle
        dt.datetime.utcnow = original_utcnow

if __name__ == "__main__":
    test_calculation()
