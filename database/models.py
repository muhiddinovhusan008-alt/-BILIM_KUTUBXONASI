"""
Ma'lumotlar bazasi so'rovlari va modellari (CRUD operatsiyalari).
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from .db import get_db


# ==================== FOYDALANUVCHILAR ====================

async def get_or_create_user(user_id: int, full_name: str, username: Optional[str] = None) -> Dict[str, Any]:
    """Foydalanuvchini oladi yoki yangisini ro'yxatdan o'tkazadi."""
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = await cursor.fetchone()
        if user:
            # Ma'lumotlarni yangilash (agar ism yoki username o'zgargan bo'lsa)
            await db.execute(
                """UPDATE users 
                   SET full_name = ?, username = ?, updated_at = CURRENT_TIMESTAMP 
                   WHERE user_id = ?""",
                (full_name, username, user_id)
            )
            await db.commit()
            cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = await cursor.fetchone()
            return dict(user)
        else:
            await db.execute(
                """INSERT INTO users (user_id, full_name, username) 
                   VALUES (?, ?, ?)""",
                (user_id, full_name, username)
            )
            await db.commit()
            cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = await cursor.fetchone()
            return dict(user)


async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Foydalanuvchi ma'lumotlarini ID orqali olish."""
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = await cursor.fetchone()
        return dict(user) if user else None


async def update_user_profile(user_id: int, full_name: Optional[str] = None, grade: Optional[str] = None):
    """Profilni tahrirlash (ism yoki sinf)."""
    async with get_db() as db:
        if full_name and grade:
            await db.execute(
                "UPDATE users SET full_name = ?, grade = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (full_name, grade, user_id)
            )
        elif full_name:
            await db.execute(
                "UPDATE users SET full_name = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (full_name, user_id)
            )
        elif grade:
            await db.execute(
                "UPDATE users SET grade = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (grade, user_id)
            )
        await db.commit()


async def is_user_subscribed_insta(user_id: int) -> bool:
    """Foydalanuvchi Instagramga obuna bo'lganligini tekshiradi."""
    async with get_db() as db:
        cursor = await db.execute("SELECT is_subscribed_insta FROM users WHERE user_id = ?", (user_id,))
        row = await cursor.fetchone()
        if row and row["is_subscribed_insta"]:
            return True
        return False


async def set_user_subscribed_insta(user_id: int):
    """Foydalanuvchi Instagram obunasini tasdiqlangan deb belgilaydi."""
    async with get_db() as db:
        await db.execute("UPDATE users SET is_subscribed_insta = 1 WHERE user_id = ?", (user_id,))
        await db.commit()


# ==================== FANLAR ====================

async def get_subjects(only_active: bool = True) -> List[Dict[str, Any]]:
    """Fanlar ro'yxatini olish."""
    async with get_db() as db:
        query = "SELECT * FROM subjects"
        if only_active:
            query += " WHERE is_active = 1"
        query += " ORDER BY id ASC"
        cursor = await db.execute(query)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_subject_by_id(subject_id: int) -> Optional[Dict[str, Any]]:
    """Fan ma'lumotlarini olish."""
    async with get_db() as db:
        cursor = await db.execute("SELECT * FROM subjects WHERE id = ?", (subject_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


async def add_subject(name: str, code: str, icon: str = "📖") -> int:
    """Yangi fan qo'shish."""
    async with get_db() as db:
        cursor = await db.execute(
            "INSERT INTO subjects (name, code, icon) VALUES (?, ?, ?)",
            (name, code, icon)
        )
        await db.commit()
        return cursor.lastrowid


# ==================== KITOBLAR VA DARSLIKLAR ====================

async def get_books_by_subject(subject_id: int) -> List[Dict[str, Any]]:
    """Fanga tegishli barcha kitoblar ro'yxati."""
    async with get_db() as db:
        cursor = await db.execute(
            """SELECT b.*, s.name as subject_name 
               FROM books b 
               JOIN subjects s ON b.subject_id = s.id 
               WHERE b.subject_id = ? 
               ORDER BY b.id DESC""",
            (subject_id,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_book_by_id(book_id: int) -> Optional[Dict[str, Any]]:
    """Aynan bitta kitob ma'lumotlari."""
    async with get_db() as db:
        cursor = await db.execute(
            """SELECT b.*, s.name as subject_name 
               FROM books b 
               JOIN subjects s ON b.subject_id = s.id 
               WHERE b.id = ?""",
            (book_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def search_books(query: str) -> List[Dict[str, Any]]:
    """Kitoblar orasidan nom yoki muallif bo'yicha qidirish."""
    async with get_db() as db:
        param = f"%{query}%"
        cursor = await db.execute(
            """SELECT b.*, s.name as subject_name, s.icon as subject_icon
               FROM books b 
               JOIN subjects s ON b.subject_id = s.id 
               WHERE b.title LIKE ? OR b.author LIKE ? OR b.description LIKE ?
               ORDER BY b.id DESC LIMIT 20""",
            (param, param, param)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def add_book(
    subject_id: int,
    title: str,
    author: str = "Noma'lum",
    grade: str = "Barcha sinflar",
    description: str = "",
    file_id: Optional[str] = None,
    file_url: Optional[str] = None
) -> int:
    """Yangi kitob yoki PDF qo'shish."""
    async with get_db() as db:
        cursor = await db.execute(
            """INSERT INTO books (subject_id, title, author, grade, description, file_id, file_url)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (subject_id, title, author, grade, description, file_id, file_url)
        )
        await db.commit()
        return cursor.lastrowid


async def increment_book_downloads(book_id: int):
    """Kitob yuklab olinish hisoblagichini 1 taga oshirish."""
    async with get_db() as db:
        await db.execute("UPDATE books SET downloads_count = downloads_count + 1 WHERE id = ?", (book_id,))
        await db.commit()


# ==================== TEST SAVOLLARI VA TEST TIZIMI ====================

async def get_questions_by_subject(subject_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """Fanga doir tasodifiy test savollarini olish."""
    async with get_db() as db:
        cursor = await db.execute(
            """SELECT * FROM questions 
               WHERE subject_id = ? 
               ORDER BY RANDOM() LIMIT ?""",
            (subject_id, limit)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_all_questions_by_subject(subject_id: int) -> List[Dict[str, Any]]:
    """Fanning barcha savollari (admin uchun)."""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM questions WHERE subject_id = ? ORDER BY id DESC",
            (subject_id,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def add_question(
    subject_id: int,
    question_text: str,
    option_a: str,
    option_b: str,
    option_c: str,
    option_d: str,
    correct_option: str,
    explanation: str = ""
) -> int:
    """Yangi test savoli qo'shish."""
    async with get_db() as db:
        cursor = await db.execute(
            """INSERT INTO questions 
               (subject_id, question_text, option_a, option_b, option_c, option_d, correct_option, explanation)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (subject_id, question_text, option_a, option_b, option_c, option_d, correct_option.upper(), explanation)
        )
        await db.commit()
        return cursor.lastrowid


async def delete_question(question_id: int) -> bool:
    """Savolni o'chirish."""
    async with get_db() as db:
        cursor = await db.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        await db.commit()
        return cursor.rowcount > 0


async def save_test_result(user_id: int, subject_id: int, total_questions: int, correct_answers: int) -> int:
    """Test natijasini saqlaydi va foydalanuvchining umumiy ballini oshiradi."""
    score = correct_answers * 2  # Har bir to'g'ri javob uchun 2 ball

    async with get_db() as db:
        # Natijani test_results jadvaliga yozish
        await db.execute(
            """INSERT INTO test_results (user_id, subject_id, total_questions, correct_answers, score)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, subject_id, total_questions, correct_answers, score)
        )
        # Foydalanuvchi profiliga qo'shish
        await db.execute(
            """UPDATE users 
               SET total_score = total_score + ?,
                   tests_count = tests_count + 1,
                   updated_at = CURRENT_TIMESTAMP
               WHERE user_id = ?""",
            (score, user_id)
        )
        await db.commit()
    return score


# ==================== O'QUVCHILAR REYTINGI ====================

async def get_top_users(limit: int = 10) -> List[Dict[str, Any]]:
    """Umumiy eng yuqori ball to'plagan o'quvchilar."""
    async with get_db() as db:
        cursor = await db.execute(
            """SELECT user_id, full_name, grade, total_score, tests_count 
               FROM users 
               ORDER BY total_score DESC, tests_count DESC 
               LIMIT ?""",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_weekly_top_users(limit: int = 10) -> List[Dict[str, Any]]:
    """Oxirgi 7 kundagi eng yaxshi natijaga ega o'quvchilar."""
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    async with get_db() as db:
        cursor = await db.execute(
            """SELECT u.user_id, u.full_name, u.grade, 
                      SUM(tr.score) as weekly_score,
                      COUNT(tr.id) as weekly_tests
               FROM test_results tr
               JOIN users u ON tr.user_id = u.user_id
               WHERE tr.completed_at >= ?
               GROUP BY u.user_id
               ORDER BY weekly_score DESC, weekly_tests DESC
               LIMIT ?""",
            (one_week_ago, limit)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_most_active_users(limit: int = 10) -> List[Dict[str, Any]]:
    """Eng ko'p test ishlagan faol o'quvchilar."""
    async with get_db() as db:
        cursor = await db.execute(
            """SELECT user_id, full_name, grade, total_score, tests_count 
               FROM users 
               ORDER BY tests_count DESC, total_score DESC 
               LIMIT ?""",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def get_user_rank(user_id: int) -> Dict[str, Any]:
    """Foydalanuvchining umumiy reytingdagi o'rni."""
    async with get_db() as db:
        # Foydalanuvchining o'z balli
        user_cursor = await db.execute("SELECT total_score FROM users WHERE user_id = ?", (user_id,))
        user_row = await user_cursor.fetchone()
        if not user_row:
            return {"rank": 0, "total_users": 0}

        score = user_row["total_score"]

        # Undan yuqoriroq ball olganlar soni
        rank_cursor = await db.execute("SELECT COUNT(*) as higher_count FROM users WHERE total_score > ?", (score,))
        rank_row = await rank_cursor.fetchone()
        higher_count = rank_row["higher_count"] if rank_row else 0

        # Jami foydalanuvchilar
        total_cursor = await db.execute("SELECT COUNT(*) as total FROM users")
        total_row = await total_cursor.fetchone()
        total_users = total_row["total"] if total_row else 0

        return {
            "rank": higher_count + 1,
            "total_users": total_users
        }


# ==================== KUNLIK BILIM ====================

async def get_daily_fact(subject_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Tasodifiy ilmiy fakt olish (yoki ma'lum fanga oid)."""
    async with get_db() as db:
        if subject_id:
            cursor = await db.execute(
                """SELECT df.*, s.name as subject_name, s.icon as subject_icon
                   FROM daily_facts df
                   LEFT JOIN subjects s ON df.subject_id = s.id
                   WHERE df.subject_id = ?
                   ORDER BY RANDOM() LIMIT 1""",
                (subject_id,)
            )
        else:
            cursor = await db.execute(
                """SELECT df.*, s.name as subject_name, s.icon as subject_icon
                   FROM daily_facts df
                   LEFT JOIN subjects s ON df.subject_id = s.id
                   ORDER BY RANDOM() LIMIT 1"""
            )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def add_daily_fact(title: str, content: str, subject_id: Optional[int] = None) -> int:
    """Yangi fakt qo'shish."""
    async with get_db() as db:
        cursor = await db.execute(
            "INSERT INTO daily_facts (subject_id, title, content) VALUES (?, ?, ?)",
            (subject_id, title, content)
        )
        await db.commit()
        return cursor.lastrowid


async def get_daily_question(date_str: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Bugungi kunlik bilim savolini olish."""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    async with get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM daily_questions WHERE date_str = ? AND is_active = 1",
            (date_str,)
        )
        row = await cursor.fetchone()
        if not row:
            # Agar bugungi sana uchun savol bo'lmasa, eng so'nggi faol savolni olish
            cursor = await db.execute(
                "SELECT * FROM daily_questions WHERE is_active = 1 ORDER BY id DESC LIMIT 1"
            )
            row = await cursor.fetchone()
        return dict(row) if row else None


async def has_user_answered_daily(user_id: int, daily_question_id: int) -> bool:
    """Foydalanuvchi ushbu kunlik savolga javob berganmi?"""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id FROM daily_answers WHERE user_id = ? AND daily_question_id = ?",
            (user_id, daily_question_id)
        )
        row = await cursor.fetchone()
        return bool(row)


async def record_daily_answer(
    user_id: int,
    daily_question_id: int,
    answered_option: str,
    is_correct: bool,
    points: int = 5
) -> bool:
    """Kunlik savol javobini qayd qilish va to'g'ri bo'lsa ball berish."""
    async with get_db() as db:
        await db.execute(
            """INSERT OR IGNORE INTO daily_answers 
               (user_id, daily_question_id, answered_option, is_correct)
               VALUES (?, ?, ?, ?)""",
            (user_id, daily_question_id, answered_option, 1 if is_correct else 0)
        )
        if is_correct:
            await db.execute(
                "UPDATE users SET total_score = total_score + ? WHERE user_id = ?",
                (points, user_id)
            )
        await db.commit()
    return is_correct


async def add_daily_question(
    question_text: str,
    option_a: str,
    option_b: str,
    option_c: str,
    option_d: str,
    correct_option: str,
    points: int = 5,
    date_str: Optional[str] = None
) -> int:
    """Yangi kunlik savol qo'shish."""
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")

    async with get_db() as db:
        cursor = await db.execute(
            """INSERT INTO daily_questions 
               (question_text, option_a, option_b, option_c, option_d, correct_option, points, date_str)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (question_text, option_a, option_b, option_c, option_d, correct_option.upper(), points, date_str)
        )
        await db.commit()
        return cursor.lastrowid


# ==================== ADMIN BILAN BOG'LANISH VA STATISTIKA ====================

async def save_contact_message(user_id: int, message_text: str) -> int:
    """Admin uchun yuborilgan murojaatni saqlash."""
    async with get_db() as db:
        cursor = await db.execute(
            "INSERT INTO contact_messages (user_id, message_text) VALUES (?, ?)",
            (user_id, message_text)
        )
        await db.commit()
        return cursor.lastrowid


async def get_bot_statistics() -> Dict[str, Any]:
    """Botning to'liq statistikasi."""
    async with get_db() as db:
        # Foydalanuvchilar soni
        u_cur = await db.execute("SELECT COUNT(*) as cnt FROM users")
        users_count = (await u_cur.fetchone())["cnt"]

        # Kitoblar soni
        b_cur = await db.execute("SELECT COUNT(*) as cnt FROM books")
        books_count = (await b_cur.fetchone())["cnt"]

        # Fanlar soni
        s_cur = await db.execute("SELECT COUNT(*) as cnt FROM subjects WHERE is_active = 1")
        subjects_count = (await s_cur.fetchone())["cnt"]

        # Savollar soni
        q_cur = await db.execute("SELECT COUNT(*) as cnt FROM questions")
        questions_count = (await q_cur.fetchone())["cnt"]

        # Ishlangan testlar soni
        tr_cur = await db.execute("SELECT COUNT(*) as cnt FROM test_results")
        tests_count = (await tr_cur.fetchone())["cnt"]

        # Umumiy berilgan ballar
        sc_cur = await db.execute("SELECT SUM(total_score) as sm FROM users")
        sc_row = await sc_cur.fetchone()
        total_scores = sc_row["sm"] if sc_row and sc_row["sm"] else 0

        # Kitoblar yuklab olinishlar soni
        dl_cur = await db.execute("SELECT SUM(downloads_count) as dl FROM books")
        dl_row = await dl_cur.fetchone()
        total_downloads = dl_row["dl"] if dl_row and dl_row["dl"] else 0

        return {
            "users_count": users_count,
            "books_count": books_count,
            "subjects_count": subjects_count,
            "questions_count": questions_count,
            "tests_count": tests_count,
            "total_scores": total_scores,
            "total_downloads": total_downloads
        }


async def get_all_user_ids() -> List[int]:
    """Barcha foydalanuvchilar ID lari (broadcast uchun)."""
    async with get_db() as db:
        cursor = await db.execute("SELECT user_id FROM users")
        rows = await cursor.fetchall()
        return [row["user_id"] for row in rows]
