from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.config import load_config
from app.db import get_order, update_order_status, increase_stock, get_all_user_ids
from app.states import BroadcastStates

router = Router()
config = load_config()


def is_admin(user_id: int) -> bool:
    return user_id in config.admin_ids


@router.callback_query(F.data.startswith("admin:"))
async def admin_actions(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Сиз админ эмассиз", show_alert=True)
        return

    try:
        _, action, order_id_raw = callback.data.split(":")
        order_id = int(order_id_raw)
    except ValueError:
        await callback.answer("Нотўғри сўров", show_alert=True)
        return

    order = get_order(order_id)
    if not order:
        await callback.answer("Буюртма топилмади", show_alert=True)
        return

    user_id = order["telegram_user_id"]

    if action == "approve":
        update_order_status(order_id, "approved")
        await callback.bot.send_message(
            user_id,
            "✅ БУЮРТМАНГИЗ АДМИН ТОМОНИДАН ТАСДИҚЛАНДИ.\nТез орада сиз билан боғланамиз."
        )
        await callback.answer("Тасдиқланди")
        return

    if action == "contacted":
        update_order_status(order_id, "contacted")
        await callback.bot.send_message(
            user_id,
            "📞 ОПЕРАТОР СИЗНИНГ БУЮРТМАНГИЗ БЎЙИЧА БОҒЛАНДИ."
        )
        await callback.answer("Белгиланди")
        return

    if action == "shipped":
        update_order_status(order_id, "shipped")
        await callback.bot.send_message(
            user_id,
            "🚚 БУЮРТМАНГИЗ ЮБОРИЛДИ.\nТез орада манзилингизга етказилади."
        )
        await callback.answer("Юборилди")
        return

    if action == "cancel":
        if order["status"] != "cancelled":
            increase_stock(order["product_slug"], 1)
        update_order_status(order_id, "cancelled")
        await callback.bot.send_message(
            user_id,
            "❌ БУЮРТМАНГИЗ БЕКОР ҚИЛИНДИ."
        )
        await callback.answer("Бекор қилинди")
        return

    await callback.answer("Номаълум амал", show_alert=True)


@router.message(Command("sendall"))
async def start_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("Сиз админ эмассиз.")
        return

    await message.answer(
        "📢 Ҳаммага юбориладиган хабарни киритинг.\n\n"
        "Бекор қилиш учун: /cancel_broadcast"
    )
    await state.set_state(BroadcastStates.waiting_for_message)


@router.message(Command("cancel_broadcast"))
async def cancel_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("Сиз админ эмассиз.")
        return

    await state.clear()
    await message.answer("❌ Рассылка бекор қилинди.")


@router.message(BroadcastStates.waiting_for_message)
async def send_broadcast(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("Сиз админ эмассиз.")
        return

    user_ids = get_all_user_ids()

    if not user_ids:
        await message.answer("Фойдаланувчилар топилмади.")
        await state.clear()
        return

    success_count = 0
    fail_count = 0

    for user_id in user_ids:
        try:
            await message.bot.send_message(user_id, message.text)
            success_count += 1
        except Exception:
            fail_count += 1

    await message.answer(
        f"✅ Рассылка якунланди.\n\n"
        f"Юборилди: {success_count}\n"
        f"Бор мади: {fail_count}"
    )
    await state.clear()
