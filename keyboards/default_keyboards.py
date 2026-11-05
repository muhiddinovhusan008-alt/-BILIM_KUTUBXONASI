"""
Asosiy pastki klaviatura (ReplyKeyboardMarkup).
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_keyboard(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Asosiy menyu tugmalari."""
    keyboard = [
        [
            KeyboardButton(text="📚 Elektron kutubxona"),
            KeyboardButton(text="📝 Test ishlash")
        ],
        [
            KeyboardButton(text="🏆 O‘quvchilar reytingi"),
            KeyboardButton(text="💡 Kunlik bilim")
        ],
        [
            KeyboardButton(text="👤 Mening profilim"),
            KeyboardButton(text="📩 Admin bilan bog‘lanish")
        ]
    ]

    # Agar foydalanuvchi admin bo'lsa, maxsus tugma qo'shiladi
    if is_admin:
        keyboard.append([KeyboardButton(text="⚙️ Admin panel")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Quyidagi bo'limlardan birini tanlang..."
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Jarayonni bekor qilish uchun Reply klaviatura."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )
