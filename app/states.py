from aiogram.fsm.state import StatesGroup, State


class OrderState(StatesGroup):
    user_id_code = State()
    full_name = State()
    product = State()
    phone = State()
    country = State()
    region = State()
    address = State()
