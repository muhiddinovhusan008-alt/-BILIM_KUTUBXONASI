"""
Kunlik bilim moduli:
Kunlik ilmiy faktlar, kunlik savol (viktorina),
fanlar bo'yicha qiziqarli ma'lumotlar.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from database import (
    get_daily_fact,
    get_daily_question,
    has_user_answered_daily,
    record_daily_answer,
    get_subject_by_id
)
from keyboards import (
    get_daily_menu_keyboard,
    get_daily_question_keyboard,
    get_subjects_keyboard
)
from utils import escape_html

router = Router()


@router.message(F.text == "💡 Kunlik bilim")
async def show_daily_menu(message: Message):
    """Kunlik bilim asosiy menyusi."""
    text = (
        "<b>💡 KUNLIK BILIM VA FAKTLAR</b>\n\n"
        "Har kuni o'z dunyoqarashingizni kengaytiring:\n\n"
        "🔬 <b>Bugungi ilmiy fakt:</b> Qiziqarli va hayratlanarli ilmiy kashfiyotlar.\n"
        "❓ <b>Kunlik bilim savoli:</b> Har kuni 1 ta maxsus savol. To'g'ri javob berib, <b>+5 ball</b> ga ega bo'ling!\n"
        "📚 <b>Fanlar bo'yicha faktlar:</b> Istalgan fan bo'yicha ajoyib ma'lumotlarni o'qing.\n\n"
        "<i>Kerakli bo'limni tanlang:</i>"
    )
    await message.answer(text, reply_markup=get_daily_menu_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "back_to_daily")
async def back_to_daily_menu(call: CallbackQuery):
    """Kunlik bilim menyusiga qaytish."""
    text = (
        "<b>💡 KUNLIK BILIM VA FAKTLAR</b>\n\n"
        "<i>Quyidagi bo'limlardan birini tanlang:</i>"
    )
    await call.message.edit_text(text, reply_markup=get_daily_menu_keyboard(), parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data == "daily:fact")
async def show_random_daily_fact(call: CallbackQuery):
    """Bugungi ilmiy faktni ko'rsatish."""
    fact = await get_daily_fact()

    if not fact:
        await call.answer("Bugun uchun ilmiy fakt topilmadi!", show_alert=True)
        return

    title = escape_html(fact["title"])
    content = escape_html(fact["content"])
    sub_name = escape_html(fact.get("subject_name", "Ilm-fan"))
    sub_icon = fact.get("subject_icon", "🔬")

    text = (
        f"{sub_icon} <b>KUN ILMIY FAKTI</b>\n"
        f"📂 <i>Fan: {sub_name}</i>\n\n"
        f"✨ <b>{title}</b>\n\n"
        f"{content}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<i>💡 Yangi ma'lumot olish uchun yana bir bor 'Boshqa fakt' tugmasini bosing!</i>"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="🎲 Boshqa fakt", callback_data="daily:fact")
    builder.button(text="🔙 Ortga qaytish", callback_data="back_to_daily")
    builder.adjust(1)

    await call.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data == "daily:subjects")
async def show_subjects_for_facts(call: CallbackQuery):
    """Fanlar bo'yicha faktlarni o'qish uchun fanni tanlash."""
    text = (
        "<b>📚 QAYSI FAN BO'YICHA FAKT O'QIMOQCHISIZ?</b>\n\n"
        "<i>Quyidagi fanlardan birini tanlang:</i>"
    )
    await call.message.edit_text(text, reply_markup=get_subjects_keyboard(action_prefix="sub_facts"), parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data.startswith("sub_facts:"))
async def show_fact_by_subject(call: CallbackQuery):
    """Tanlangan fanga doir faktni ko'rsatish."""
    subject_id = int(call.data.split(":")[1])
    fact = await get_daily_fact(subject_id=subject_id)
    subject = await get_subject_by_id(subject_id)

    sub_name = escape_html(subject["name"]) if subject else "Fan"
    sub_icon = subject["icon"] if subject else "🔬"

    if not fact:
        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 Fanlar ro'yxatiga", callback_data="daily:subjects")
        await call.message.edit_text(
            f"{sub_icon} <b>{sub_name}</b> bo'yicha hozircha faktlar kiritilmagan.\nTez orada qo'shiladi!",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        await call.answer()
        return

    title = escape_html(fact["title"])
    content = escape_html(fact["content"])

    text = (
        f"{sub_icon} <b>{sub_name} HAQIDA QIZIQARLI FAKT</b>\n\n"
        f"✨ <b>{title}</b>\n\n"
        f"{content}"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="🎲 Yana bitta fakt", callback_data=f"sub_facts:{subject_id}")
    builder.button(text="🔙 Fanlar ro'yxatiga", callback_data="daily:subjects")
    builder.adjust(1)

    await call.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data == "daily:question")
async def show_daily_question(call: CallbackQuery):
    """Kunlik savolni ko'rsatish."""
    user_id = call.from_user.id
    daily_q = await get_daily_question()

    if not daily_q:
        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 Ortga", callback_data="back_to_daily")
        await call.message.edit_text(
            "Bugun uchun kunlik bilim savoli hali joylanmagan.\nKechroq yana tekshirib ko'ring!",
            reply_markup=builder.as_markup()
        )
        await call.answer()
        return

    q_id = daily_q["id"]
    has_answered = await has_user_answered_daily(user_id=user_id, daily_question_id=q_id)

    if has_answered:
        builder = InlineKeyboardBuilder()
        builder.button(text="🔙 Kunlik bilimga qaytish", callback_data="back_to_daily")
        await call.message.edit_text(
            "✅ <b>Siz bugungi kunlik bilim savoliga javob berib bo'lgansiz!</b>\n\n"
            "Ertaga yangi savol va yangi ballar sizni kutmoqda. O'z bilimingizni sinash uchun umumiy test bo'limidan foydalanishingiz mumkin.",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
        await call.answer()
        return

    text = (
        f"❓ <b>KUNLIK BILIM SAVOLI</b> (Mukofot: <b>+{daily_q['points']} ball</b>)\n\n"
        f"<b>{escape_html(daily_q['question_text'])}</b>\n\n"
        f"<b>A)</b> {escape_html(daily_q['option_a'])}\n"
        f"<b>B)</b> {escape_html(daily_q['option_b'])}\n"
        f"<b>C)</b> {escape_html(daily_q['option_c'])}\n"
        f"<b>D)</b> {escape_html(daily_q['option_d'])}\n\n"
        f"<i>To'g'ri javobni tanlang (faqat 1 ta imkoniyat!):</i>"
    )

    await call.message.edit_text(
        text,
        reply_markup=get_daily_question_keyboard(q_id),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data.startswith("daily_ans:"))
async def process_daily_answer(call: CallbackQuery):
    """Kunlik savol javobini tekshirish va ball berish."""
    parts = call.data.split(":")
    q_id = int(parts[1])
    selected_option = parts[2].upper()
    user_id = call.from_user.id

    # Qayta tekshirish
    already = await has_user_answered_daily(user_id=user_id, daily_question_id=q_id)
    if already:
        await call.answer("Siz bu savolga allaqachon javob bergansiz!", show_alert=True)
        return

    daily_q = await get_daily_question()
    if not daily_q or daily_q["id"] != q_id:
        await call.answer("Savol ma'lumoti topilmadi!", show_alert=True)
        return

    is_correct = (selected_option == daily_q["correct_option"].upper())
    points = daily_q["points"]

    await record_daily_answer(
        user_id=user_id,
        daily_question_id=q_id,
        answered_option=selected_option,
        is_correct=is_correct,
        points=points
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="🏆 Reytingni ko'rish", callback_data="rating:top")
    builder.button(text="🔙 Kunlik bilimga qaytish", callback_data="back_to_daily")
    builder.adjust(1)

    if is_correct:
        result_text = (
            f"🎉 <b>TABRIKLAYMIZ, TO'G'RI JAVOB!</b>\n\n"
            f"Sizning javobingiz: <b>{selected_option}</b>\n"
            f"Sizga <b>+{points} ball</b> taqdim etildi va profilingizga qo'shildi! ⭐️"
        )
    else:
        correct = daily_q["correct_option"].upper()
        result_text = (
            f"❌ <b>Afsuski, javobingiz noto'g'ri.</b>\n\n"
            f"Siz tanlagan variant: <b>{selected_option}</b>\n"
            f"To'g'ri javob: <b>{correct}</b>\n\n"
            f"<i>Xafa bo'lmang! Ertaga yangi savolda o'z omadingizni sinab ko'ring.</i>"
        )

    await call.message.edit_text(result_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await call.answer()
