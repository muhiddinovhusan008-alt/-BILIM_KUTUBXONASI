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
async def start_insta_verification(call: CallbackQuery, state: FSMContext):
    """Instagram obunasini tasdiqlash uchun username yoki skrinshot so'rash."""
    await state.set_state(InstagramVerifyStates.waiting_for_proof)

    text = (
        "📸 <b>INSTAGRAM OBUNASINI TASDIQLASH</b>\n\n"
        "Hurmatli o'quvchi! @muh1dd1nov_ai sahifasiga obuna bo‘lganingizni tasdiqlash uchun:\n\n"
        "1️⃣ O'zingizning <b>Instagram foydalanuvchi nomingizni (Username)</b> yozib yuboring (masalan: <code>@username</code> yoki <code>muhiddinov</code>);\n"
        "2️⃣ Yoki sahifaga obuna bo‘lganingiz aks etgan <b>skrinshot (rasm)</b> yuboring!\n\n"
        "<i>Administrator tekshirib tasdiqlashi bilan bot menyusi darhol ochiladi.</i>"
    )

    cancel_btn = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_insta_verify")]
        ]
    )

    await call.message.edit_text(text, reply_markup=cancel_btn, parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data == "cancel_insta_verify")
async def cancel_insta_verification(call: CallbackQuery, state: FSMContext):
    """Instagram tasdiqlashni bekor qilish."""
    await state.clear()
    text = (
        "⚠️ <b>Botdan to‘liq foydalanish uchun bizning rasmiy Instagram sahifamizga obuna bo‘lishingiz kerak!</b>\n\n"
        "1️⃣ Pastdagi tugma orqali sahifamizga o‘ting va obuna bo‘ling;\n"
        "2️⃣ So‘ngra <b>«✅ Obunani tasdiqlash»</b> tugmasini bosing."
    )
    await call.message.edit_text(text, reply_markup=get_instagram_sub_keyboard(), parse_mode="HTML")
    await call.answer()


@router.message(InstagramVerifyStates.waiting_for_proof)
async def process_insta_proof(message: Message, state: FSMContext, bot: Bot):
    """Foydalanuvchi Instagram username yoki skrinshot yuborganida adminga yetkazish."""
    await state.clear()
    user_id = message.from_user.id
    full_name = escape_html(message.from_user.full_name or "O'quvchi")
    username = f"@{message.from_user.username}" if message.from_user.username else "Mavjud emas"

    proof_info = ""
    if message.text:
        proof_info = f"📸 <b>Instagram akkaunt:</b> <code>{escape_html(message.text.strip())}</code>"
    elif message.caption:
        proof_info = f"📸 <b>Instagram akkaunt / izoh:</b> {escape_html(message.caption.strip())}"
    else:
        proof_info = "📸 <b>Obuna skrinshoti yuborildi</b>"

    # Foydalanuvchiga kuting xabari (bot menyusi hali OCHILMAYDI!)
    await message.answer(
        "⏳ <b>So‘rovingiz administratorga yuborildi!</b>\n\n"
        "Administrator (@Muhiddinov_official) obunangizni tekshirib tasdiqlashi bilanoq bot menyusi siz uchun to‘liq ochiladi. Iltimos, ozgina kuting!",
        parse_mode="HTML"
    )

    # Adminga tasdiqlash / rad etish tugmalari
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Tasdiqlash (Botni ochish)", callback_data=f"insta_adm_ok:{user_id}")
    builder.button(text="❌ Rad etish (Yolg'on)", callback_data=f"insta_adm_no:{user_id}")
    builder.adjust(1)

    admin_notification = (
        "🔔 <b>YANGI INSTAGRAM OBUNA TASDIQLASH SO‘ROVI!</b>\n\n"
        f"👤 <b>O‘quvchi:</b> {full_name}\n"
        f"🔗 <b>Telegram:</b> {username}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"{proof_info}\n\n"
        "<i>Haqiqatan ham @muh1dd1nov_ai sahifasiga obuna bo‘lganmi?</i>"
    )

    for admin_id in ADMIN_IDS:
        try:
            if message.photo:
                # Agar skrinshot bo'lsa, rasmni adminga jo'natish
                await bot.send_photo(
                    chat_id=admin_id,
                    photo=message.photo[-1].file_id,
                    caption=admin_notification,
                    reply_markup=builder.as_markup(),
                    parse_mode="HTML"
                )
            else:
                await bot.send_message(
                    chat_id=admin_id,
                    text=admin_notification,
                    reply_markup=builder.as_markup(),
                    parse_mode="HTML"
                )
        except Exception:
            pass


@router.callback_query(F.data.startswith("insta_adm_ok:"))
async def admin_approve_insta(call: CallbackQuery, bot: Bot):
    """Admin foydalanuvchi obunasini tasdiqlaganda chaqiriladi."""
    target_user_id = int(call.data.split(":")[1])

    # Bazada obunani tasdiqlash
    await set_user_subscribed_insta(target_user_id, is_sub=True)

    # Foydalanuvchiga botni ochish va xabar berish
    try:
        welcome_text = (
            "🎉 <b>TABRIKLAYMIZ! INSTAGRAM OBUNANGIZ TASDIQLANDI!</b>\n\n"
            "Administrator obunangizni muvaffaqiyatli tasdiqladi. «Bilim Kutubxonasi» botining barcha imkoniyatlaridan to‘liq foydalanishingiz mumkin! 🎓\n\n"
            "O‘zingizga kerakli bo‘limni tanlang:"
        )
        await bot.send_message(
            chat_id=target_user_id,
            text=welcome_text,
            reply_markup=get_main_keyboard(is_admin=is_admin(target_user_id)),
            parse_mode="HTML"
        )
    except Exception:
        pass

    await call.message.edit_caption(
        caption=f"{call.message.caption or call.message.text}\n\n✅ <b>TASDIQLANDI! Foydalanuvchiga bot menyusi ochildi.</b>",
        reply_markup=None,
        parse_mode="HTML"
    ) if call.message.photo else await call.message.edit_text(
        text=f"{call.message.text}\n\n✅ <b>TASDIQLANDI! Foydalanuvchiga bot menyusi ochildi.</b>",
        reply_markup=None,
        parse_mode="HTML"
    )
    await call.answer("Foydalanuvchi tasdiqlandi!")


@router.callback_query(F.data.startswith("insta_adm_no:"))
async def admin_reject_insta(call: CallbackQuery, bot: Bot):
    """Admin foydalanuvchi obunasini rad etganda chaqiriladi."""
    target_user_id = int(call.data.split(":")[1])

    # Bazada obunani 0 qilish
    await set_user_subscribed_insta(target_user_id, is_sub=False)

    # Foydalanuvchiga rad etilganini bildirish
    try:
        reject_text = (
            "❌ <b>KECHIRASIZ, OBUNANGIZ TASDIQLANMADI!</b>\n\n"
            "Administrator tekshirdi, siz @muh1dd1nov_ai sahifasiga obuna bo‘lmagansiz yoki noto‘g‘ri ma'lumot yuborgansiz.\n\n"
            "Iltimos, avval haqiqatdan sahifamizga obuna bo‘ling va qayta tasdiqlash uchun so‘rov yuboring!"
        )
        await bot.send_message(
            chat_id=target_user_id,
            text=reject_text,
            reply_markup=get_instagram_sub_keyboard(),
            parse_mode="HTML"
        )
    except Exception:
        pass

    await call.message.edit_caption(
        caption=f"{call.message.caption or call.message.text}\n\n❌ <b>RAD ETILDI! Foydalanuvchiga obuna rad etilgani bildirildi.</b>",
        reply_markup=None,
        parse_mode="HTML"
    ) if call.message.photo else await call.message.edit_text(
        text=f"{call.message.text}\n\n❌ <b>RAD ETILDI! Foydalanuvchiga obuna rad etilgani bildirildi.</b>",
        reply_markup=None,
        parse_mode="HTML"
    )
    await call.answer("So'rov rad etildi!")


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
