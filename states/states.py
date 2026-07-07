"""
states/states.py

FSM-состояния проекта.
"""

from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    """
    Пользовательские состояния.
    """

    waiting_screenshot = State()


class AdminStates(StatesGroup):
    """
    Состояния администратора.
    """

    # -------------------------
    # Тексты
    # -------------------------

    waiting_start_text = State()

    waiting_instruction_text = State()

    waiting_thank_you_text = State()

    waiting_presave_url = State()

    waiting_button_text = State()

    waiting_screenshot_button_text = State()

    waiting_broadcast_text = State()

    waiting_channel_username = State()

    waiting_channel_title = State()

    waiting_new_admin_id = State()



    # -------------------------
    # Розыгрыш
    # -------------------------

    waiting_broadcast_date = State()

    waiting_winners_count = State()

    # -------------------------
    # Рассылка
    # -------------------------

    waiting_broadcast_message = State()
