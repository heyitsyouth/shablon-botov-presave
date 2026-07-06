"""
states.py

FSM-состояния Telegram-бота.

Используются aiogram 3.x.
"""

from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    """
    Состояния пользователя.
    """

    waiting_for_screenshot = State()


class AdminStates(StatesGroup):
    """
    Состояния администратора.
    """

    waiting_start_text = State()

    waiting_instruction_text = State()

    waiting_button_text = State()

    waiting_presave_url = State()

    waiting_thank_you_text = State()

    waiting_broadcast_text = State()

    waiting_draw_date = State()

    waiting_winner_count = State()

    waiting_broadcast_message = State()

    waiting_search_query = State()
