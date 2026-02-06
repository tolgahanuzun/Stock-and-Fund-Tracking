# Borsa & Fon Takip Uygulaması

Hisse ve fon portföylerini takip etmek için basit, hafif bir web uygulaması.

[🇺🇸 English README](README.md)

## Ekran Görüntüleri

| Ana Sayfa (Dashboard) | Yönetim Paneli (Admin) |
|:---:|:---:|
| <img src="img/index.png" alt="Ana Sayfa" width="400"/> | <img src="img/admin.png" alt="Admin Paneli" width="400"/> |

## Teknoloji Altyapısı

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite, APScheduler
- **Frontend:** HTML, CSS (Bootstrap), Vanilla JavaScript
- **Veri Kaynağı:** TEFAS (crawler ile)

## Temel Özellikler

- **Varlık Yönetimi:** Admin panelinden fon/hisse ekleme ve düzenleme.
- **Portföy Takibi:** Adet, maliyet ve güncel değer takibi.
- **Otomatik Veri:** Günlük TEFAS veri çekme işlemleri (Background job).
- **Grafikler:** Chart.js ile tarihsel fiyat grafikleri.
- **Çoklu Dil:** İngilizce ve Türkçe desteği (Frontend & Admin).

## Kurulum

1. **Klonla ve Hazırla:**
   ```bash
   git clone <repo-url>
   cd borsa-takip
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Çalıştır:**
   ```bash
   uvicorn backend.main:app --reload
   ```

3. **Erişim:**
   - Uygulama: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - Admin: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

## Yapılacaklar Listesi (Todo)

- [ ] Mobil Uygulama (React Native/Flutter)
- [ ] Telegram Bot Bildirimleri
- [ ] Kullanıcı Girişi (JWT Auth)
- [ ] Yabancı Hisse & Kripto Desteği
- [ ] Veri Dışa Aktarma (CSV/Excel)
