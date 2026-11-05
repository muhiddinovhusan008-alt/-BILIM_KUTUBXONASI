"""
Yordamchi funksiyalar: matnni formatlash, admin tekshiruvi, baholash mezonlari.
"""

import html
from typing import List, Dict, Any
from config import ADMIN_IDS


def is_admin(user_id: int) -> bool:
    """Foydalanuvchi administrator ekanligini tekshiradi."""
    return user_id in ADMIN_IDS


def escape_html(text: str) -> str:
    """HTML maxsus belgilarini xavfsiz qiladi."""
    if not text:
        return ""
    return html.escape(str(text))


def format_user_profile(user: Dict[str, Any], rank_info: Dict[str, Any]) -> str:
    """Foydalanuvchi profilini chiroyli tarzda shakllantiradi."""
    full_name = escape_html(user.get("full_name", "Noma'lum"))
    grade = escape_html(user.get("grade", "Ko'rsatilmagan"))
    tests_count = user.get("tests_count", 0)
    total_score = user.get("total_score", 0)
    rank = rank_info.get("rank", 0)
    total_users = rank_info.get("total_users", 0)

    rank_display = f"{rank}-o'rin (jami {total_users} o'quvchi ichida)" if rank > 0 else "Aniqlanmagan"

    text = (
        "<b>👤 SHAXSIY PROFILINGIZ</b>\n\n"
        f"🏷 <b>Ism-familiya:</b> {full_name}\n"
        f"🎓 <b>Sinfingiz:</b> {grade}\n"
        f"📝 <b>Ishlangan testlar:</b> {tests_count} ta\n"
        f"⭐️ <b>To'plagan ballaringiz:</b> {total_score} ball\n"
        f"🏆 <b>Reytingdagi o'rningiz:</b> {rank_display}\n\n"
        "<i>Ma'lumotlaringizni tahrirlash uchun quyidagi tugmalardan foydalanishingiz mumkin:</i>"
    )
    return text


def format_rating_list(users: List[Dict[str, Any]], title: str, is_weekly: bool = False, is_active: bool = False) -> str:
    """Reyting ro'yxatini chiroyli ko'rinishga keltiradi."""
    if not users:
        return f"<b>{title}</b>\n\nHozircha ma'lumotlar mavjud emas."

    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    lines = [f"<b>{title}</b>\n"]

    for idx, u in enumerate(users):
        medal = medals[idx] if idx < len(medals) else f"{idx+1}."
        name = escape_html(u.get("full_name", "O'quvchi"))
        grade = escape_html(u.get("grade", ""))
        grade_text = f" ({grade})" if grade and grade != "Ko'rsatilmagan" else ""

        if is_weekly:
            score = u.get("weekly_score", 0)
            tests = u.get("weekly_tests", 0)
            lines.append(f"{medal} <b>{name}</b>{grade_text} — <b>{score} ball</b> (<i>{tests} ta test</i>)")
        elif is_active:
            tests = u.get("tests_count", 0)
            score = u.get("total_score", 0)
            lines.append(f"{medal} <b>{name}</b>{grade_text} — <b>{tests} ta test</b> (<i>{score} ball</i>)")
        else:
            score = u.get("total_score", 0)
            tests = u.get("tests_count", 0)
            lines.append(f"{medal} <b>{name}</b>{grade_text} — <b>{score} ball</b> (<i>{tests} ta test</i>)")

    lines.append("\n<i>🏆 Har kuni test ishlab, ballaringizni oshiring va reytingda 1-o'ringa chiqing!</i>")
    return "\n".join(lines)


def get_score_appraisal(percent: float) -> str:
    """Test natijasi foiziga qarab baho va rag'batlantiruvchi xabar beradi."""
    if percent >= 90:
        return "🌟 <b>A'LO!</b> Siz ushbu fanni juda chuqur o'zlashtirgansiz. Barakalla!"
    elif percent >= 70:
        return "👍 <b>YAXSHI!</b> Natijangiz ancha yuqori, xatolar ustida ishlab yana-da yaxshiroq natijaga erishing."
    elif percent >= 50:
        return "👌 <b>QONIQARLI!</b> Mavzuni qaytadan takrorlab, kitoblarni o'qib chiqishingizni maslahat beramiz."
    else:
        return "💪 <b>DAVOM ETING!</b> Taslim bo'lmang, elektron kutubxonadagi darsliklardan o'rganib qayta urinib ko'ring!"
