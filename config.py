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

# Telegram Bot Token
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

# Ixtiyoriy proksi
PROXY_URL = os.getenv("PROXY_URL", "").strip() or None

# ==================== WEBHOOK VA VIRTUAL SERVER SOZLAMALARI ====================
# Render avtomatik ravishda RENDER_EXTERNAL_URL taqdim etadi (masalan: https://bilim-bot.onrender.com)
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "").strip()
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").strip() or RENDER_EXTERNAL_URL

WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook").strip()
if not WEBHOOK_PATH.startswith("/"):
    WEBHOOK_PATH = f"/{WEBHOOK_PATH}"

# Telegram Webhook xavfsizligi uchun maxfiy kalit (Secret Token)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "bilim_kutubxonasi_secret_token_key").strip()

# Render Web Service tinglaydigan port va xost
PORT = int(os.getenv("PORT", 10000))
HOST = os.getenv("HOST", "0.0.0.0")
