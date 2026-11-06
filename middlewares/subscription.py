"""
Instagram obunasini majburiy tekshirish middleware moduli.
Foydalanuvchi obunani tasdiqlamaguncha bot funksiyalaridan foydalana olmaydi.
"""

from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from database import is_user_subscribed_insta, get_or_create_user
from keyboards import get_instagram_sub_keyboard
from utils import is_admin, escape_html


class InstagramSubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user = data.get("event_from_user")
        if not user:
            return await handler(event, data)

        user_id = user.id

        # Foydalanuvchini bazaga qo'shish / yangilash
        await get_or_create_user(
            user_id=user_id,
            full_name=user.full_name or "O'quvchi",
            username=user.username
        )

        # Administratorlarga cheklov qo'yilmaydi
        if is_admin(user_id):
            return await handler(event, data)

        # Adminning tasdiqlash/rad etish tugmalariga ruxsat berish
        if isinstance(event, CallbackQuery) and event.data and (event.data.startswith("insta_adm_ok:") or event.data.startswith("insta_adm_no:")):
            return await handler(event, data)

        # Agar foydalanuvchi "Obunani tasdiqlash" tugmasini bosayotgan bo'lsa, o'tkaziladi
        if isinstance(event, CallbackQuery) and event.data == "check_insta_sub":
            return await handler(event, data)

        # Agar foydalanuvchi Instagram ma'lumotlarini (skrinshot yoki username) yuborayotgan bo'lsa, o'tkaziladi
        state = data.get("state")
        if state:
            current_state = await state.get_state()
            if current_state == "InstagramVerifyStates:waiting_for_proof":
                return await handler(event, data)

        # Obunani bazadan tekshirish
        is_sub = await is_user_subscribed_insta(user_id)
        if is_sub:
            return await handler(event, data)

        # Agar hali obuna bo'lmagan bo'lsa
        sub_text = (
            f"Assalomu alaykum, <b>{escape_html(user.full_name or 'O‘quvchi')}</b>!\n\n"
            f"<b>«BILIM KUTUBXONASI»</b> platformasiga xush kelibsiz! 🎓\n\n"
            f"⚠️ <b>Botdan to‘liq foydalanish uchun bizning rasmiy Instagram sahifamizga obuna bo‘lishingiz kerak!</b>\n\n"
            f"1️⃣ Pastdagi <b>«📲 Instagram sahifaga obuna bo‘lish»</b> tugmasi orqali sahifamizga obuna bo‘ling;\n"
            f"2️⃣ So‘ngra <b>«✅ Obunani tasdiqlash»</b> tugmasini bosing."
        )

        if isinstance(event, Message):
            await event.answer(
                text=sub_text,
                reply_markup=get_instagram_sub_keyboard(),
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            return
        elif isinstance(event, CallbackQuery):
            await event.answer(
                "⚠️ Botdan foydalanish uchun avval Instagram sahifamizga obuna bo'ling!",
                show_alert=True
            )
            return

        return await handler(event, data)
