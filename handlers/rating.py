"""
O'quvchilar reytingi moduli:
Umumiy top, haftalik top, faol o'quvchilar va shaxsiy o'rin.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database import (
    get_top_users,
    get_weekly_top_users,
    get_most_active_users,
    get_user,
    get_user_rank
)
from keyboards import get_rating_menu_keyboard
from utils import format_rating_list, escape_html

router = Router()


@router.message(F.text == "🏆 O‘quvchilar reytingi")
async def show_rating_menu(message: Message):
    """Reyting bo'limining asosiy menyusi."""
    text = (
        "<b>🏆 O'QUVCHILAR REYTINGI</b>\n\n"
        "Bilim va faollik bo'yicha tengdoshlaringiz natijalari bilan tanishing:\n\n"
        "🔸 <b>Umumiy Top-10:</b> Barcha vaqtlar davomida eng ko'p ball to'plaganlar\n"
        "🔸 <b>Haftalik Top-10:</b> Ushbu haftadagi eng yaxshi natijalar\n"
        "🔸 <b>Eng faollar:</b> Eng ko'p test yechgan o'quvchilar\n"
        "🔸 <b>Mening o'rnim:</b> Shaxsiy reytingingiz va o'rningiz\n\n"
        "<i>Kerakli bo'limni tanlang:</i>"
    )
    await message.answer(text, reply_markup=get_rating_menu_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "rating:top")
async def callback_top_rating(call: CallbackQuery):
    """Umumiy Top-10 o'quvchilar."""
    users = await get_top_users(limit=10)
    text = format_rating_list(users, "🏆 UMUMIY TOP-10 O'QUVCHILAR", is_weekly=False)
    await call.message.edit_text(text, reply_markup=get_rating_menu_keyboard(), parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data == "rating:weekly")
async def callback_weekly_rating(call: CallbackQuery):
    """Haftalik Top-10 o'quvchilar."""
    users = await get_weekly_top_users(limit=10)
    text = format_rating_list(users, "📅 HAFTALIK TOP-10 O'QUVCHILAR", is_weekly=True)
    await call.message.edit_text(text, reply_markup=get_rating_menu_keyboard(), parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data == "rating:active")
async def callback_active_rating(call: CallbackQuery):
    """Eng ko'p test yechgan o'quvchilar."""
    users = await get_most_active_users(limit=10)
    text = format_rating_list(users, "⚡️ ENG FAOL O'QUVCHILAR", is_active=True)
    await call.message.edit_text(text, reply_markup=get_rating_menu_keyboard(), parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data == "rating:my_rank")
async def callback_my_rank(call: CallbackQuery):
    """Foydalanuvchining o'z o'rni."""
    user = await get_user(call.from_user.id)
    rank_info = await get_user_rank(call.from_user.id)

    full_name = escape_html(user.get("full_name", "O'quvchi")) if user else "O'quvchi"
    score = user.get("total_score", 0) if user else 0
    tests = user.get("tests_count", 0) if user else 0
    grade = escape_html(user.get("grade", "Ko'rsatilmagan")) if user else "Ko'rsatilmagan"

    rank = rank_info.get("rank", 0)
    total = rank_info.get("total_users", 0)

    text = (
        "<b>📍 SIZNING REYTINGDAGI O'RNINGIZ</b>\n\n"
        f"👤 <b>O'quvchi:</b> {full_name}\n"
        f"🎓 <b>Sinf:</b> {grade}\n"
        f"⭐️ <b>To'plagan ball:</b> {score} ball\n"
        f"📝 <b>Yechilgan testlar:</b> {tests} ta\n\n"
        f"🏆 <b>O'rningiz:</b> <b>{rank}-o'rin</b> (Jami {total} nafar o'quvchi orasida)\n\n"
        "<i>Har kuni yangi testlar va kunlik savollarga javob berib, reytingingizni yanada oshiring!</i>"
    )
    await call.message.edit_text(text, reply_markup=get_rating_menu_keyboard(), parse_mode="HTML")
    await call.answer()
