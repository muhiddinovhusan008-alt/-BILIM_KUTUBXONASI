"""
Inline tugmalar (InlineKeyboardMarkup).
"""

from typing import List, Dict, Any, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_subjects_keyboard(action_prefix: str = "sub_lib") -> InlineKeyboardMarkup:
    """
    Fanlar ro'yxatini chiqaruvchi inline klaviatura.
    action_prefix:
    - 'sub_lib' (kutubxona uchun)
    - 'sub_quiz' (test uchun)
    - 'sub_facts' (faktlar uchun)
    - 'adm_book_sub' (admin kitob qo'shishi uchun)
    - 'adm_q_sub' (admin savol qo'shishi uchun)
    """
    builder = InlineKeyboardBuilder()

    # 10 ta asosiy fanlar
    subjects = [
        ("📐 Matematika", 1),
        ("⚡ Fizika", 2),
        ("🧪 Kimyo", 3),
        ("🌿 Biologiya", 4),
        ("🏛 Tarix", 5),
        ("✍️ Ona tili", 6),
        ("📜 Adabiyot", 7),
        ("🇬🇧 Ingliz tili", 8),
        ("🌍 Geografiya", 9),
        ("💻 Informatika", 10),
    ]

    for name, s_id in subjects:
        builder.button(text=name, callback_data=f"{action_prefix}:{s_id}")

    builder.adjust(2)  # Har qatorda 2 tadan tugma

    if action_prefix == "sub_lib":
        # Qidirish tugmasi
        builder.row(InlineKeyboardButton(text="🔍 Kitob qidirish", callback_data="search_books"))

    builder.row(InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_main"))

    return builder.as_markup()


def get_books_keyboard(books: List[Dict[str, Any]], subject_id: int) -> InlineKeyboardMarkup:
    """Fanga tegishli kitoblar ro'yxati inline tugmalari."""
    builder = InlineKeyboardBuilder()

    for book in books:
        # Kitob nomi va sinfi
        title_btn = f"📖 {book['title']} ({book['grade']})"
        builder.button(text=title_btn, callback_data=f"book_info:{book['id']}")

    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="🔙 Fanlar ro'yxatiga qaytish", callback_data="back_to_subjects_lib"))
    return builder.as_markup()


def get_book_action_keyboard(book_id: int, subject_id: int, has_file: bool = False, file_url: Optional[str] = None) -> InlineKeyboardMarkup:
    """Kitobni ko'rish yoki yuklab olish harakatlari."""
    builder = InlineKeyboardBuilder()

    if has_file:
        builder.button(text="📥 Kitobni yuklab olish (PDF)", callback_data=f"download_book:{book_id}")
    elif file_url:
        builder.button(text="🌐 Onlayn o'qish (Havola)", url=file_url)
    else:
        builder.button(text="📥 Faylni qabul qilish", callback_data=f"download_book:{book_id}")

    builder.row(InlineKeyboardButton(text="🔙 Kitoblar ro'yxatiga", callback_data=f"sub_lib:{subject_id}"))
    return builder.as_markup()


def get_quiz_count_keyboard(subject_id: int) -> InlineKeyboardMarkup:
    """Test savollari sonini tanlash (10, 20, 30 ta)."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔹 10 ta savol", callback_data=f"start_quiz:{subject_id}:10")
    builder.button(text="🔹 20 ta savol", callback_data=f"start_quiz:{subject_id}:20")
    builder.button(text="🔹 30 ta savol", callback_data=f"start_quiz:{subject_id}:30")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="🔙 Fanlar ro'yxatiga qaytish", callback_data="back_to_subjects_quiz"))
    return builder.as_markup()


def get_quiz_options_keyboard(current_index: int, total_count: int) -> InlineKeyboardMarkup:
    """Testdagi 4 ta javob varianti (A, B, C, D)."""
    builder = InlineKeyboardBuilder()
    builder.button(text="A", callback_data="ans:A")
    builder.button(text="B", callback_data="ans:B")
    builder.button(text="C", callback_data="ans:C")
    builder.button(text="D", callback_data="ans:D")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="🛑 Testni to'xtatish", callback_data="stop_quiz"))
    return builder.as_markup()


def get_rating_menu_keyboard() -> InlineKeyboardMarkup:
    """O'quvchilar reytingi bo'limi inline menyusi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🏆 Umumiy Top-10", callback_data="rating:top")
    builder.button(text="📅 Haftalik Top-10", callback_data="rating:weekly")
    builder.button(text="⚡️ Eng faollar", callback_data="rating:active")
    builder.button(text="📍 Mening o'rnim", callback_data="rating:my_rank")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_main"))
    return builder.as_markup()


def get_daily_menu_keyboard() -> InlineKeyboardMarkup:
    """Kunlik bilim bo'limi menyusi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔬 Bugungi ilmiy fakt", callback_data="daily:fact")
    builder.button(text="❓ Kunlik bilim savoli (+5 ball)", callback_data="daily:question")
    builder.button(text="📚 Fanlar bo'yicha faktlar", callback_data="daily:subjects")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_main"))
    return builder.as_markup()


def get_daily_question_keyboard(daily_q_id: int) -> InlineKeyboardMarkup:
    """Kunlik savolga javob variantlari."""
    builder = InlineKeyboardBuilder()
    builder.button(text="A", callback_data=f"daily_ans:{daily_q_id}:A")
    builder.button(text="B", callback_data=f"daily_ans:{daily_q_id}:B")
    builder.button(text="C", callback_data=f"daily_ans:{daily_q_id}:C")
    builder.button(text="D", callback_data=f"daily_ans:{daily_q_id}:D")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="🔙 Kunlik bilimga qaytish", callback_data="back_to_daily"))
    return builder.as_markup()


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Shaxsiy profil menyusi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Ismni o'zgartirish", callback_data="edit_profile:name")
    builder.button(text="🎓 Sinfni o'zgartirish", callback_data="edit_profile:grade")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="back_to_main"))
    return builder.as_markup()


def get_admin_main_keyboard() -> InlineKeyboardMarkup:
    """Admin boshqaruv paneli menyusi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 To'liq statistika", callback_data="admin:stats")
    builder.button(text="📚 Kitob / PDF yuklash", callback_data="admin:add_book")
    builder.button(text="📝 Test savoli qo'shish", callback_data="admin:add_question")
    builder.button(text="🗑 Test savolini o'chirish", callback_data="admin:del_question")
    builder.button(text="💡 Ilmiy fakt qo'shish", callback_data="admin:add_fact")
    builder.button(text="❓ Kunlik savol qo'shish", callback_data="admin:add_daily_q")
    builder.button(text="📢 Barchaga xabar (Broadcast)", callback_data="admin:broadcast")
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="🔙 Asosiy menyuga qaytish", callback_data="back_to_main"))
    return builder.as_markup()


def get_admin_cancel_keyboard() -> InlineKeyboardMarkup:
    """Admin amalini bekor qilish."""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Bekor qilish", callback_data="admin:cancel")
    return builder.as_markup()


def get_back_keyboard(callback_data: str) -> InlineKeyboardMarkup:
    """Oddiy orqaga qaytish tugmasi."""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 Ortga", callback_data=callback_data)
    return builder.as_markup()
