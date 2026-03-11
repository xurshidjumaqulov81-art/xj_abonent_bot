from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    waiting_for_id = State()
    waiting_for_full_name = State()
    waiting_for_product = State()
    waiting_for_phone = State()
    waiting_for_country = State()
    waiting_for_region = State()
    waiting_for_address = State()
    waiting_for_review = State()


class BroadcastStates(StatesGroup):
    waiting_for_message = State()
