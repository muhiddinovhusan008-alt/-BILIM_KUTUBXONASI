"""
Test tizimi moduli:
Fanlar bo'yicha testlar, 10, 20 va 30 talik variantlar,
javoblarni tekshirish, natijalarni hisoblash va saqlash.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from database import (
    get_subject_by_id,
    get_questions_by_subject,
    save_test_result
)
from keyboards import (
    get_subjects_keyboard,
    get_quiz_count_keyboard,
    get_quiz_options_keyboard,
    get_main_keyboard
)
from states import QuizStates
from utils import escape_html, get_score_appraisal, is_admin

router = Router()


@router.message(F.text == "📝 Test ishlash")
async def show_quiz_subjects(message: Message, state: FSMContext):
    """Test topshirish uchun fanni tanlash."""
    await state.clear()
    text = (
        "<b>📝 TEST TIZIMI</b>\n\n"
        "Bilimingizni sinash uchun qaysi fandan test topshirmoqchisiz?\n"
        "<i>Quyidagi fanlardan birini tanlang:</i>"
    )
    await message.answer(text, reply_markup=get_subjects_keyboard(action_prefix="sub_quiz"), parse_mode="HTML")


@router.callback_query(F.data == "back_to_subjects_quiz")
async def back_to_subjects_quiz(call: CallbackQuery, state: FSMContext):
    """Fanlar ro'yxatiga qaytish."""
    await state.clear()
    text = (
        "<b>📝 TEST TIZIMI</b>\n\n"
        "Bilimingizni sinash uchun qaysi fandan test topshirmoqchisiz?\n"
        "<i>Quyidagi fanlardan birini tanlang:</i>"
    )
    await call.message.edit_text(text, reply_markup=get_subjects_keyboard(action_prefix="sub_quiz"), parse_mode="HTML")
    await call.answer()


@router.callback_query(F.data.startswith("sub_quiz:"))
async def choose_quiz_length(call: CallbackQuery):
    """Savollar sonini tanlash (10, 20, 30 ta)."""
    subject_id = int(call.data.split(":")[1])
    subject = await get_subject_by_id(subject_id)

    sub_name = subject["name"] if subject else "Fan"
    sub_icon = subject["icon"] if subject else "📝"

    text = (
        f"{sub_icon} <b>{sub_name}</b> fanidan test sinovi.\n\n"
        f"Nechta savoldan iborat test ishlamoqchisiz?\n"
        f"<i>Variantlardan birini tanlang:</i>"
    )
    await call.message.edit_text(
        text,
        reply_markup=get_quiz_count_keyboard(subject_id),
        parse_mode="HTML"
    )
    await call.answer()


@router.callback_query(F.data.startswith("start_quiz:"))
async def start_quiz_session(call: CallbackQuery, state: FSMContext):
    """Test jarayonini boshlash."""
    parts = call.data.split(":")
    subject_id = int(parts[1])
    desired_count = int(parts[2])

    questions = await get_questions_by_subject(subject_id=subject_id, limit=desired_count)

    if not questions:
        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text="🔙 Boshqa fanni tanlash", callback_data="back_to_subjects_quiz"))
        await call.message.edit_text(
            "Ushbu fan bo'yicha hozircha test savollari mavjud emas.\n"
            "Administrator tez orada savollarni kiritadi.",
            reply_markup=builder.as_markup()
        )
        await call.answer()
        return

    subject = await get_subject_by_id(subject_id)
    subject_name = subject["name"] if subject else "Fan"

    # FSM ma'lumotlarini o'rnatish
    await state.set_state(QuizStates.answering)
    await state.update_data(
        subject_id=subject_id,
        subject_name=subject_name,
        questions=questions,
        current_index=0,
        total_questions=len(questions),
        correct_count=0,
        wrong_count=0,
        user_answers=[]
    )

    await send_next_question(call.message, state, is_edit=True)
    await call.answer()


async def send_next_question(message: Message, state: FSMContext, is_edit: bool = False):
    """Navbatdagi savolni foydalanuvchiga yuborish."""
    data = await state.get_data()
    questions = data.get("questions", [])
    idx = data.get("current_index", 0)
    total = data.get("total_questions", len(questions))
    subject_name = data.get("subject_name", "Fan")

    if idx >= len(questions):
        # Test yakunlandi!
        await finish_quiz(message, state, is_edit=is_edit)
        return

    q = questions[idx]
    q_num = idx + 1

    text = (
        f"📝 <b>Fan:</b> {escape_html(subject_name)}\n"
        f"📊 <b>Savol:</b> {q_num}/{total}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"❓ <b>{escape_html(q['question_text'])}</b>\n\n"
        f"<b>A)</b> {escape_html(q['option_a'])}\n"
        f"<b>B)</b> {escape_html(q['option_b'])}\n"
        f"<b>C)</b> {escape_html(q['option_c'])}\n"
        f"<b>D)</b> {escape_html(q['option_d'])}\n\n"
        f"<i>To'g'ri deb hisoblagan variantingizni tanlang:</i>"
    )

    markup = get_quiz_options_keyboard(current_index=q_num, total_count=total)

    if is_edit:
        try:
            await message.edit_text(text, reply_markup=markup, parse_mode="HTML")
        except Exception:
            await message.answer(text, reply_markup=markup, parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=markup, parse_mode="HTML")


@router.callback_query(QuizStates.answering, F.data.startswith("ans:"))
async def process_quiz_answer(call: CallbackQuery, state: FSMContext):
    """Foydalanuvchi javobini qabul qilish va keyingi savolga o'tish."""
    selected_option = call.data.split(":")[1].upper()
    data = await state.get_data()

    questions = data.get("questions", [])
    idx = data.get("current_index", 0)
    correct_count = data.get("correct_count", 0)
    wrong_count = data.get("wrong_count", 0)
    user_answers = data.get("user_answers", [])

    if idx < len(questions):
        current_q = questions[idx]
        correct_opt = current_q["correct_option"].upper()
        is_correct = (selected_option == correct_opt)

        if is_correct:
            correct_count += 1
        else:
            wrong_count += 1

        user_answers.append({
            "question": current_q["question_text"],
            "selected": selected_option,
            "correct": correct_opt,
            "is_correct": is_correct
        })

    # Indeksni 1 taga oshirish
    await state.update_data(
        current_index=idx + 1,
        correct_count=correct_count,
        wrong_count=wrong_count,
        user_answers=user_answers
    )

    await send_next_question(call.message, state, is_edit=True)
    await call.answer()


@router.callback_query(QuizStates.answering, F.data == "stop_quiz")
async def stop_quiz_handler(call: CallbackQuery, state: FSMContext):
    """Testni muddatidan oldin to'xtatish."""
    await finish_quiz(call.message, state, is_edit=True, is_stopped=True)
    await call.answer("Test to'xtatildi!")


async def finish_quiz(message: Message, state: FSMContext, is_edit: bool = False, is_stopped: bool = False):
    """Test natijalarini hisoblash, bazada saqlash va hisobot berish."""
    data = await state.get_data()
    user_id = message.chat.id
    subject_id = data.get("subject_id", 1)
    subject_name = data.get("subject_name", "Fan")
    correct_count = data.get("correct_count", 0)
    wrong_count = data.get("wrong_count", 0)
    total_answered = correct_count + wrong_count

    if total_answered == 0:
        total_answered = 1  # Nolga bo'linmasligi uchun

    percent = round((correct_count / total_answered) * 100, 1)

    # Natijani bazaga saqlash va profilga ball qo'shish
    score_earned = 0
    if correct_count > 0:
        score_earned = await save_test_result(
            user_id=user_id,
            subject_id=subject_id,
            total_questions=total_answered,
            correct_answers=correct_count
        )

    await state.clear()
    appraisal = get_score_appraisal(percent)

    status_title = "🛑 <b>TEST TO'XTATILDI</b>" if is_stopped else "🏁 <b>TEST YAKUNLANDI!</b>"

    text = (
        f"{status_title}\n\n"
        f"📂 <b>Fan:</b> {escape_html(subject_name)}\n"
        f"📊 <b>Jami ishlangan savollar:</b> {total_answered} ta\n"
        f"✅ <b>To'g'ri javoblar:</b> {correct_count} ta\n"
        f"❌ <b>Noto'g'ri javoblar:</b> {wrong_count} ta\n"
        f"📈 <b>Natija:</b> {percent}%\n"
        f"⭐️ <b>To'plangan ball:</b> +{score_earned} ball\n\n"
        f"{appraisal}\n\n"
        f"<i>Ballaringiz shaxsiy profilingizga qo'shildi va umumiy reytingda yangilandi!</i>"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Qayta test ishlash", callback_data=f"start_quiz:{subject_id}:{total_answered}")
    builder.button(text="📚 Kutubxonaga o'tish", callback_data=f"sub_lib:{subject_id}")
    builder.button(text="🏆 Reytingni ko'rish", callback_data="rating:top")
    builder.button(text="🔙 Asosiy menyu", callback_data="back_to_main")
    builder.adjust(1)

    if is_edit:
        try:
            await message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
        except Exception:
            await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
