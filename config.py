"""
Konfiguratsiya moduli:
.env faylidan sozlamalarni yuklaydi va tekshiradi.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Loyihaning asosiy katalogi
BASE_DIR = Path(__file__).resolve().parent

# .env faylini yuklash
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Adminlar ID ro'yxati (masalan: "123456,7891011" -> [123456, 7891011])
admin_ids_raw = os.getenv("ADMIN_IDS", "").strip()
ADMIN_IDS = []
if admin_ids_raw:
    for item in admin_ids_raw.split(","):
        item = item.strip()
        if item.isdigit():
            ADMIN_IDS.append(int(item))

# Baza fayli joylashuvi
DB_PATH = BASE_DIR / os.getenv("DATABASE_PATH", "database/bilim_kutubxonasi.db")

# Darslik va kitoblar uchun yuklash papkasi
MEDIA_DIR = BASE_DIR / "media"
BOOKS_DIR = MEDIA_DIR / "books"
BOOKS_DIR.mkdir(parents=True, exist_ok=True)

# Ixtiyoriy proksi (masalan: http://proxy_user:proxy_pass@ip:port yoki socks5://...)
PROXY_URL = os.getenv("PROXY_URL", "").strip() or None
