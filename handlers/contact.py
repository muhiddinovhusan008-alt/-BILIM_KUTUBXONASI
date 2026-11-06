"""
Admin bilan bog'lanish moduli:
Foydalanuvchilarga administrator bilan bog'lanish havolasini (@Muhiddinov_official) yuboradi.
"""

from aiogram import Router, F
from aiogram.types import Message

from keyboards import get_contact_admin_keyboard

router = Router()


@router.message(F.text == "📩 Admin bilan bog‘lanish")
async def show_admin_contact(message: Message):
    """Admin bilan bog'lanish havolasini yuborish."""
    text = (
        "<b>📩 ADMINISTRATOR BILAN BOG'LANISH</b>\n\n"
        "Savollaringiz, takliflaringiz yoki murojaatlaringiz bo'lsa, administrator bilan to'g'ridan-to'g'ri bog'lanishingiz mumkin:\n\n"
        "👤 <b>Administrator:</b> @Muhiddinov_official\n"
        "🔗 <b>Bog'lanish havolasi:</b> https://t.me/Muhiddinov_official\n\n"
        "<i>Quyidagi tugmani bosib, bevosita xabar yozishingiz mumkin:</i>"
    )
    await message.answer(
        text=text,
        reply_markup=get_contact_admin_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
