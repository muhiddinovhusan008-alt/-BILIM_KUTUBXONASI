"""
Admin bilan bog'lanish moduli:
Foydalanuvchilarning taklif va murojaatlarini qabul qilish hamda adminga yo'naltirish.
"""

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from database import save_contact_message
from keyboards import get_main_keyboard, get_cancel_keyboard
from states import ContactStates
from utils import escape_html, is_admin

router = Router()


@router.message(F.text == "📩 Admin bilan bog‘lanish")
async def start_contact(message: Message, state: FSMContext):
    """Admin bilan bog'lanish jarayonini boshlash."""
    await state.set_state(ContactStates.waiting_for_message)
    text = (
        "<b>📩 ADMINISTRATORGA MUROJAAT</b>\n\n"
        "Takliflaringiz, savollaringiz yoki bot bo'yicha fikrlaringiz bormi?\n"
        "Xabaringizni yozib qoldiring, administratorlarimiz tez orada uni ko'rib chiqishadi:\n\n"
        "<i>Bekor qilish uchun pastdagi '❌ Bekor qilish' tugmasini bosing.</i>"
    )
    await message.answer(text, reply_markup=get_cancel_keyboard(), parse_mode="HTML")


@router.message(ContactStates.waiting_for_message)
async def process_contact_message(message: Message, state: FSMContext, bot: Bot):
    """Foydalanuvchi xabarini qabul qilish va adminga yuborish."""
    text_content = message.text or message.caption or ""

    if not text_content and not message.document and not message.photo:
        await message.answer("Iltimos, matnli xabar yoki fayl yuboring:")
        return

    user_id = message.from_user.id
    full_name = escape_html(message.from_user.full_name)
    username = f"@{message.from_user.username}" if message.from_user.username else "Yo'q"

    # Bazaga saqlash
    await save_contact_message(user_id=user_id, message_text=text_content or "[Fayl/Media]")
    await state.clear()

    # Barcha adminlarga yuborish
    admin_notification = (
        f"📩 <b>YANGI MUROJAAT!</b>\n\n"
        f"👤 <b>Kimdan:</b> {full_name}\n"
        f"🔗 <b>Username:</b> {username}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
        f"💬 <b>Xabar matni:</b>\n{escape_html(text_content)}"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(chat_id=admin_id, text=admin_notification, parse_mode="HTML")
            # Agar rasm yoki hujjat bo'lsa, uni ham nusxasini forward qilish
            if message.photo:
                await bot.send_photo(chat_id=admin_id, photo=message.photo[-1].file_id)
            elif message.document:
                await bot.send_document(chat_id=admin_id, document=message.document.file_id)
        except Exception:
            pass

    admin_flag = is_admin(user_id)
    await message.answer(
        "✅ <b>Xabaringiz administratorga muvaffaqiyatli yetkazildi!</b>\n\n"
        "E'tiboringiz va taklifingiz uchun tashakkur.",
        reply_markup=get_main_keyboard(is_admin=admin_flag),
        parse_mode="HTML"
    )
