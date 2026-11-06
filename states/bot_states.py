"""
FSM (Finite State Machine) holatlari.
"""

from aiogram.fsm.state import State, StatesGroup


class EditProfileStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_grade = State()


class SearchBookStates(StatesGroup):
    waiting_for_query = State()


class ContactStates(StatesGroup):
    waiting_for_message = State()


class QuizStates(StatesGroup):
    answering = State()


class InstagramVerifyStates(StatesGroup):
    waiting_for_proof = State()


# Admin uchun holatlar
class AdminAddBookStates(StatesGroup):
    waiting_for_subject = State()
    waiting_for_title = State()
    waiting_for_author = State()
    waiting_for_grade = State()
    waiting_for_desc = State()
    waiting_for_file = State()


class AdminAddQuestionStates(StatesGroup):
    waiting_for_subject = State()
    waiting_for_question_text = State()
    waiting_for_option_a = State()
    waiting_for_option_b = State()
    waiting_for_option_c = State()
    waiting_for_option_d = State()
    waiting_for_correct_option = State()
    waiting_for_explanation = State()


class AdminAddFactStates(StatesGroup):
    waiting_for_subject = State()
    waiting_for_title = State()
    waiting_for_content = State()


class AdminAddDailyQuestionStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_option_a = State()
    waiting_for_option_b = State()
    waiting_for_option_c = State()
    waiting_for_option_d = State()
    waiting_for_correct = State()
    waiting_for_points = State()


class AdminBroadcastStates(StatesGroup):
    waiting_for_message = State()
