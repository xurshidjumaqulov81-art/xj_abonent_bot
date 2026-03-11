from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.states import OrderState
from app.keyboards import products_keyboard
from app.texts import ERROR_TEXT

router = Router()


@router.message(F.text == "🚀 БОШЛАШ")
async def start_order(message: Message, state: FSMContext):
    await message.answer(
        "🆔 Илтимос 7 хонали ID рақамингизни киритинг\n\nНамуна: 0012345"
    )
    await state.set_state(OrderState.user_id_code)


@router.message(OrderState.user_id_code)
async def get_id(message: Message, state: FSMContext):

    if not message.text.isdigit() or len(message.text) != 7:
        await message.answer(ERROR_TEXT)
        return

    await state.update_data(user_id_code=message.text)

    await message.answer(
        "👤 Исм фамилиянгизни киритинг\n\nНамуна: Алиев Сардор"
    )

    await state.set_state(OrderState.full_name)


@router.message(OrderState.full_name)
async def get_name(message: Message, state: FSMContext):

    if len(message.text.split()) < 2:
        await message.answer(ERROR_TEXT)
        return

    await state.update_data(full_name=message.text)

    await message.answer(
        "🛍 Маҳсулотни танланг",
        reply_markup=products_keyboard
    )

    await state.set_state(OrderState.product)


@router.message(OrderState.product)
async def get_product(message: Message, state: FSMContext):

    await state.update_data(product=message.text)

    await message.answer(
        "📱 Телефон рақамингизни киритинг\n\nНамуна: +998901234567"
    )

    await state.set_state(OrderState.phone)


@router.message(OrderState.phone)
async def get_phone(message: Message, state: FSMContext):

    if not message.text.startswith("+998"):
        await message.answer(ERROR_TEXT)
        return

    await state.update_data(phone=message.text)

    await message.answer(
        "🌍 Давлатингизни ёзинг"
    )

    await state.set_state(OrderState.country)


@router.message(OrderState.country)
async def get_country(message: Message, state: FSMContext):

    await state.update_data(country=message.text)

    await message.answer("📍 Вилоятигизни ёзинг")

    await state.set_state(OrderState.region)


@router.message(OrderState.region)
async def get_region(message: Message, state: FSMContext):

    await state.update_data(region=message.text)

    await message.answer(
        "🏠 Аниқ манзилингизни ёзинг"
    )

    await state.set_state(OrderState.address)


@router.message(OrderState.address)
async def finish_order(message: Message, state: FSMContext):

    await state.update_data(address=message.text)

    data = await state.get_data()

    text = f"""
✅ БУЮРТМА ҚАБУЛ ҚИЛИНДИ

🆔 ID: {data['user_id_code']}
👤 ИСМ: {data['full_name']}
🧴 МАҲСУЛОТ: {data['product']}
📱 ТЕЛЕФОН: {data['phone']}
🌍 ДАВЛАТ: {data['country']}
📍 ВИЛОЯТ: {data['region']}
🏠 МАНЗИЛ: {data['address']}
"""

    await message.answer(text)

    await state.clear()
