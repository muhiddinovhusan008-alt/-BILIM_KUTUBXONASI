from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ADMIN_IDS
from database import (
    get_or_create_user, get_user, update_user_profile, get_user_rank,
    set_user_subscribed_insta, is_user_subscribed_insta
)
from keyboards import (
    get_main_keyboard,
    get_cancel_keyboard,
    get_profile_keyboard,
    get_subjects_keyboard,
    get_rating_menu_keyboard,
    get_daily_menu_keyboard,
    get_admin_main_keyboard,
    get_instagram_sub_keyboard
)
from states import EditProfileStates, InstagramVerifyStates
from utils import is_admin, format_user_profile, escape_html

router = Router()


@router.callback_query(F.data == "check_insta_sub")
async def process_insta_verification(call: CallbackQuery, state: FSMContext):
    """Instagram obunasini tasdiqlash tugmasi bosilganda avtomatik bot menyusini chiqarish."""
    await state.clear()
    user_id = call.from_user.id
    full_name = escape_html(call.from_user.full_name or "O'quvchi")

    # Obunani bazada tasdiqlash
    await set_user_subscribed_insta(user_id, is_sub=True)
    admin_flag = is_admin(user_id)

    try:
        await call.message.delete()
    except Exception:
        pass

    welcome_text = (
        f"🎉 <b>TABRIKLAYMIZ! OBUNANGIZ TASDIQLANDI!</b>\n\n"
        f"Assalomu alaykum, <b>{full_name}</b>!\n\n"
        f"<b>«BILIM KUTUBXONASI»</b> — zamonaviy o‘quv platformasiga xush kelibsiz! 🎓\n\n"
        f"Bu yerda siz:\n"
        f"📚 <i>Barcha fanlar bo‘yicha elektron darsliklar va kitoblarni o‘qishingiz;</i>\n"
        f"📝 <i>Bilimingizni sinash uchun turli testlarni yechishingiz;</i>\n"
        f"🏆 <i>O‘quvchilar o‘rtasida o‘z reytingingizni oshirishingiz;</i>\n"
        f"💡 <i>Har kuni qiziqarli ilmiy faktlar va savollardan xabardor bo‘lishingiz mumkin.</i>\n\n"
        f"O‘zingizga kerakli bo‘limni tanlang:"
    )

    await call.message.answer(
        text=welcome_text,
        reply_markup=get_main_keyboard(is_admin=admin_flag),
        parse_mode="HTML"
    )
    await call.answer("✅ Obunangiz tasdiqlandi! Xush kelibsiz!")



@router.message(Command("reset_sub"))
async def cmd_reset_sub(message: Message):
    """Obunani qayta sinash uchun holatni nolga tushirish (sinov uchun)."""
    await set_user_subscribed_insta(message.from_user.id, is_sub=False)
    await message.answer(
        "🔄 <b>Obunangiz holati qayta sinash uchun nolga tushirildi!</b>\n\n"
        "Endi /start buyrug'ini yuboring va obuna oynasini tekshiring.",
        parse_mode="HTML"
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Start buyrug'i qayta ishlanadi."""
    await state.clear()
    user_id = message.from_user.id
    full_name = message.from_user.full_name or "O'quvchi"
    username = message.from_user.username

    # Bazaga yozish yoki olish
    await get_or_create_user(user_id=user_id, full_name=full_name, username=username)
    admin_flag = is_admin(user_id)

    # Instagram obunasi tekshiruvi
    is_sub = await is_user_subscribed_insta(user_id)
    if not is_sub:
        sub_text = (
            f"Assalomu alaykum, <b>{escape_html(full_name)}</b>!\n\n"
            f"<b>«BILIM KUTUBXONASI»</b> platformasiga xush kelibsiz! 🎓\n\n"
            f"⚠️ <b>Botdan to‘liq foydalanish uchun bizning rasmiy Instagram sahifamizga obuna bo‘lishingiz kerak!</b>\n\n"
            f"1️⃣ Pastdagi <b>«📲 Instagram sahifaga obuna bo‘lish»</b> tugmasi orqali sahifamizga o‘ting va obuna bo‘ling;\n"
            f"2️⃣ So‘ngra <b>«✅ Obunani tasdiqlash»</b> tugmasini bosing."
        )
        await message.answer(
            text=sub_text,
            reply_markup=get_instagram_sub_keyboard(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        return

    welcome_text = (
        f"Assalomu alaykum, <b>{escape_html(full_name)}</b>!\n\n"
        f"<b>«BILIM KUTUBXONASI»</b> — zamonaviy o‘quv platformasiga xush kelibsiz! 🎓\n\n"
        f"Bu yerda siz:\n"
        f"📚 <i>Barcha fanlar bo‘yicha elektron darsliklar va kitoblarni o‘qishingiz;</i>\n"
        f"📝 <i>Bilimingizni sinash uchun turli testlarni yechishingiz;</i>\n"
        f"🏆 <i>O‘quvchilar o‘rtasida o‘z reytingingizni oshirishingiz;</i>\n"
        f"💡 <i>Har kuni qiziqarli ilmiy faktlar va savollardan xabardor bo‘lishingiz mumkin.</i>\n\n"
        f"O‘zingizga kerakli bo‘limni tanlang:"
    )

    await message.answer(
        text=welcome_text,
        reply_markup=get_main_keyboard(is_admin=admin_flag),
        parse_mode="HTML"
    )




@router.message(Command("help"))
async def cmd_help(message: Message):
    """Yordam buyrug'i."""
    help_text = (
        "<b>📖 BOTDAN FOYDALANISH BO'YICHA YO'RIQNOMA:</b>\n\n"
        "1. <b>📚 Elektron kutubxona:</b> O'zingiz qiziqqan fanni tanlang, mavjud darsliklarni ko'ring yoki qidiruv orqali kerakli adabiyotni toping.\n"
        "2. <b>📝 Test ishlash:</b> Fan va savollar sonini (10, 20 yoki 30 ta) tanlang va bilimingizni sinab ko'ring. Har bir to'g'ri javob uchun ball olasiz!\n"
        "3. <b>🏆 O‘quvchilar reytingi:</b> Eng bilimdon va faol tengdoshlaringiz ro'yxatini hamda o'zingizning o'rningizni ko'ring.\n"
        "4. <b>💡 Kunlik bilim:</b> Har kuni bitta yangi ilmiy fakt va bitta kunlik savolga javob berib, qo'shimcha ball jamg'aring.\n"
        "5. <b>👤 Mening profilim:</b> O'z ismingiz, sinfingiz va natijalaringizni ko'ring yoki tahrirlang.\n"
        "6. <b>📩 Admin bilan bog‘lanish:</b> Taklif va savollaringiz bo'lsa, adminga xabar qoldiring.\n\n"
        "<i>Har qanday muammo yoki taklif bo'lsa, bemalol murojaat qilishingiz mumkin!</i>"
    )
    await message.answer(help_text, parse_mode="HTML")


@router.message(F.text == "❌ Bekor qilish")
async def cancel_action(message: Message, state: FSMContext):
    """Joriy FSM jarayonini bekor qilish va bosh menyuga qaytish."""
    await state.clear()
    admin_flag = is_admin(message.from_user.id)
    await message.answer(
        "Amal bekor qilindi. Asosiy menyudasiz:",
        reply_markup=get_main_keyboard(is_admin=admin_flag)
    )


@router.callback_query(F.data == "back_to_main")
async def callback_back_to_main(call: CallbackQuery, state: FSMContext):
    """Inline tugma orqali asosiy menyuga qaytish."""
    await state.clear()
    admin_flag = is_admin(call.from_user.id)
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(
        "Bosh sahifadasiz. Bo'limni tanlang:",
        reply_markup=get_main_keyboard(is_admin=admin_flag)
    )
    await call.answer()


# ==================== MENING PROFILIM ====================

@router.message(F.text == "👤 Mening profilim")
async def show_profile(message: Message):
    """Foydalanuvchi profilini ko'rsatish."""
    user = await get_user(message.from_user.id)
    if not user:
        user = await get_or_create_user(
            user_id=message.from_user.id,
            full_name=message.from_user.full_name or "O'quvchi",
            username=message.from_user.username
        )

    rank_info = await get_user_rank(message.from_user.id)
    text = format_user_profile(user, rank_info)
    await message.answer(text, reply_markup=get_profile_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "edit_profile:name")
async def start_edit_name(call: CallbackQuery, state: FSMContext):
    """Ismni o'zgartirishni boshlash."""
    await state.set_state(EditProfileStates.waiting_for_name)
    await call.message.answer(
        "Iltimos, yangi <b>ism va familiyangizni</b> kiriting:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await call.answer()


@router.message(EditProfileStates.waiting_for_name)
async def process_new_name(message: Message, state: FSMContext):
    """Yangi ismni saqlash."""
    new_name = message.text.strip()
    if len(new_name) < 2 or len(new_name) > 60:
        await message.answer("Ism juda qisqa yoki juda uzun. Qaytadan kiriting:")
        return

    await update_user_profile(user_id=message.from_user.id, full_name=new_name)
    await state.clear()

    admin_flag = is_admin(message.from_user.id)
    await message.answer(
        f"✅ Ismingiz muvaffaqiyatli o'zgartirildi: <b>{escape_html(new_name)}</b>",
        reply_markup=get_main_keyboard(is_admin=admin_flag),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "edit_profile:grade")
async def start_edit_grade(call: CallbackQuery, state: FSMContext):
    """Sinfni o'zgartirishni boshlash."""
    await state.set_state(EditProfileStates.waiting_for_grade)
    await call.message.answer(
        "Iltimos, <b>sinfingizni</b> kiriting (masalan: <i>9-sinf</i> yoki <i>11-A sinf</i>):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await call.answer()


@router.message(EditProfileStates.waiting_for_grade)
async def process_new_grade(message: Message, state: FSMContext):
    """Yangi sinfni saqlash."""
    new_grade = message.text.strip()
    if len(new_grade) > 30:
        await message.answer("Sinf nomi juda uzun. Qaytadan kiriting:")
        return

    await update_user_profile(user_id=message.from_user.id, grade=new_grade)
    await state.clear()

    admin_flag = is_admin(message.from_user.id)
    await message.answer(
        f"✅ Sinfingiz muvaffaqiyatli saqlandi: <b>{escape_html(new_grade)}</b>",
        reply_markup=get_main_keyboard(is_admin=admin_flag),
        parse_mode="HTML"
    )
