"""
«BILIM KUTUBXONASI» Telegram botining asosiy ishga tushiruvchi fayli (entrypoint).
Aiogram 3 va aiosqlite asosida yaratilgan.
"""

import sys
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_IDS, PROXY_URL
from database import init_db
from handlers import setup_routers

# Logging konfiguratsiyasi
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("BilimKutubxonasi")


async def on_startup(bot: Bot):
    """Bot ishga tushganda bajariladigan amallar."""
    logger.info("Ma'lumotlar bazasi initsializatsiya qilinmoqda...")
    await init_db()
    logger.info("Ma'lumotlar bazasi tayyor!")

    try:
        bot_info = await bot.get_me()
        logger.info(f"Bot muvaffaqiyatli ulandi: @{bot_info.username} ({bot_info.first_name})")

        # Adminlarga bot ishga tushgani haqida xabarnoma
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(
                    chat_id=admin_id,
                    text=f"🚀 <b>«Bilim Kutubxonasi» boti muvaffaqiyatli ishga tushirildi!</b>\n"
                         f"🤖 Bot: @{bot_info.username}",
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.warning(f"Adminga ({admin_id}) xabar yetkazilmadi: {e}")
    except Exception as e:
        logger.error(f"Telegram serveri bilan bog'lanishda xatolik: {e}")


async def on_shutdown(bot: Bot):
    """Bot to'xtatilganda bajariladigan amallar."""
    logger.info("Bot to'xtatilmoqda...")
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text="⚠️ <b>«Bilim Kutubxonasi» boti to'xtatildi!</b>",
                parse_mode=ParseMode.HTML
            )
        except Exception:
            pass


async def main():
    """Asosiy asinxron ishga tushirish funksiyasi."""
    # Bot tokeni tekshiruvi
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE" or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error(
            "\n" + "=" * 60 + "\n"
            "XATOLIK: .env faylida BOT_TOKEN ko'rsatilmagan!\n"
            "Iltimos, .env faylidagi BOT_TOKEN ga o'z bot tokeningizni yozing.\n"
            "=" * 60
        )
        return

    # Proksi sessiyasi (agar kerak bo'lsa)
    session = None
    if PROXY_URL:
        logger.info(f"Proksi orqali ulanmoqda: {PROXY_URL}")
        session = AiohttpSession(proxy=PROXY_URL)

    # Bot va Dispatcher yaratish
    bot = Bot(
        token=BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Routerlarni ulash
    dp.include_router(setup_routers())

    # Startup va Shutdown hodisalari
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Eski kutilayotgan yangilanishlarni tozalash va pollingni boshlash
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.warning(f"Webhook tozalashda ogohlantirish: {e}")

    logger.info("Bot polling rejimida tinglashni boshlamoqda...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot qo'lda to'xtatildi.")
