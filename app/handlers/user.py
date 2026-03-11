import re
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from app.states import OrderStates
from app.texts import (
    START_TEXT,
    ERROR_TEXT,
    SUCCESS_TEXT,
    PRODUCTS,
    COUNTRIES,
    COUNTRY_REGIONS,
)
from app.keyboards import (
    start_keyboard,
    countries_keyboard,
    regions_keyboard,
    products_keyboard,
    select_product_keyboard,
    review_keyboard,
    admin_order_keyboard,
)
from app.db import (
    get_all_products,
    get_product,
    decrease_stock,
    create_order,
)
from app.config import load_config

router = Router()
config = load_config()


def valid_phone(text: str) -> bool:
    return bool(re.fullmatch(r"\+\d{10,15}", text.strip()))


def valid_full_name(text: str) -> bool:
    parts = [x for x in text.strip().split() if x]
    return len(parts) >= 2


def valid_address(text: str) -> bool:
    return len(text.strip()) >= 10


async def send_start_banner(message: Message) -> None:
    banner_path = Path("assets/start_banner.jpg")
    if banner_path.exists():
        await message.answer_photo(
            photo=FSInputFile(banner_path),
            caption=START_TEXT,
            reply_markup=start_keyboard(),
        )
    else:
        await message.answer(
            START_TEXT,
            reply_markup=start_keyboard(),
        )


async def send_catalog(target) -> None:
    products = get_all_products()
    text = (
        "🛍 <b>МАҲСУЛОТЛАР КАТАЛОГИ</b>\n\n"
        "📦 Ҳар бир маҳсулотдан <b>фақат 1 дона</b> харид қилиш мумкин.\n"
        "Қуйидаги маҳсулотлардан бирини танланг."
    )
    keyboard = products_keyboard(products)

    if isinstance(target, Message):
        await target.answer(text, reply_markup=keyboard)
    else:
        await target.message.answer(text, reply_markup=keyboard)


def build_review_text(data: dict) -> str:
    return (
        "📋 <b>ИЛТИМОС, МАЪЛУМОТЛАРНИ ТЕКШИРИНГ</b>\n\n"
        f"🆔 <b>ID:</b> {data['customer_id_code']}\n"
        f"👤 <b>ИСМ ФАМИЛИЯ:</b> {data['full_name']}\n"
        f"🧴 <b>МАҲСУЛОТ:</b> {data['product_name']}\n"
        f"📱 <b>ТЕЛЕФОН:</b> {data['phone']}\n"
        f"🌍 <b>ДАВЛАТ:</b> {data['country']}\n"
        f"📍 <b>ВИЛОЯТ:</b> {data['region']}\n"
        f"🏠 <b>МАНЗИЛ:</b> {data['address']}"
    )


def build_admin_text(
    order_id: int,
    telegram_user_id: int,
    telegram_username: str | None,
    data: dict
) -> str:
    if telegram_username:
        profile_link = f"https://t.me/{telegram_username}"
        profile_text = f'<a href="{profile_link}">@{telegram_username}</a>'
    else:
        profile_link = f"tg://user?id={telegram_user_id}"
        profile_text = f'<a href="{profile_link}">ФОЙДАЛАНУВЧИ ПРОФИЛИ</a>'

    return (
        "🛒 <b>ЯНГИ БУЮРТМА</b>\n\n"
        f"📦 <b>Буюртма рақами:</b> #{order_id}\n"
        f"🆔 <b>ID:</b> {data['customer_id_code']}\n"
        f"👤 <b>ИСМ ФАМИЛИЯ:</b> {data['full_name']}\n"
        f"📱 <b>ТЕЛЕГРАМ:</b> {profile_text}\n"
        f"🧴 <b>МАҲСУЛОТ:</b> {data['product_name']}\n"
        f"📞 <b>ҚАБУЛ ҚИЛУВЧИ РАҚАМ:</b> {data['phone']}\n"
        f"🌍 <b>ДАВЛАТ:</b> {data['country']}\n"
        f"📍 <b>ВИЛОЯТ:</b> {data['region']}\n"
        f"🏠 <b>МАНЗИЛ:</b> {data['address']}\n\n"
        f"🔗 <b>ПРОФИЛГА ЎТИШ:</b> {profile_text}"
    )


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await send_start_banner(message)


@router.message(F.text == "🚀 БОШЛАШ")
async def begin_order(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🆔 Илтимос, 7 хонали ID рақамингизни киритинг.\n"
        "📌 Намуна: <code>0012345</code>",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(OrderStates.waiting_for_id)


@router.message(OrderStates.waiting_for_id)
async def get_customer_id(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not (text.isdigit() and len(text) == 7):
        await message.answer(
            f"{ERROR_TEXT}\n\n🆔 ID рақам 7 хонали бўлиши керак.\n📌 Намуна: <code>0012345</code>"
        )
        return

    await state.update_data(customer_id_code=text)
    await message.answer(
        "👤 Илтимос, исм ва фамилиянгизни киритинг.\n"
        "📌 Намуна: <code>Алиев Сардор</code>"
    )
    await state.set_state(OrderStates.waiting_for_full_name)


@router.message(OrderStates.waiting_for_full_name)
async def get_full_name(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not valid_full_name(text):
        await message.answer(
            f"{ERROR_TEXT}\n\n👤 Исм ва фамилияни тўлиқ ёзинг.\n📌 Намуна: <code>Алиев Сардор</code>"
        )
        return

    await state.update_data(full_name=text)
    await state.set_state(OrderStates.waiting_for_product)
    await send_catalog(message)


@router.callback_query(F.data == "back_to_catalog")
async def back_to_catalog(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.waiting_for_product)

    try:
        await callback.message.delete()
    except Exception:
        pass

    await send_catalog(callback)
    await callback.answer()


@router.callback_query(OrderStates.waiting_for_product, F.data.startswith("view_product:"))
async def view_product(callback: CallbackQuery, state: FSMContext):
    slug = callback.data.split(":", 1)[1]
    product_row = get_product(slug)
    product_info = PRODUCTS.get(slug)

    if not product_row or not product_info:
        await callback.answer("Маҳсулот топилмади", show_alert=True)
        return

    text = (
        f"{product_info['description']}\n\n"
        f"📦 <b>Мавжуд сони:</b> {product_row['stock']} та\n"
        f"🛒 <b>Харид қилиш мумкин:</b> 1 дона"
    )

    photo_path = Path(product_info["photo"])
    if photo_path.exists():
        await callback.message.answer_photo(
            photo=FSInputFile(photo_path),
            caption=text,
            reply_markup=select_product_keyboard(slug),
        )
    else:
        await callback.message.answer(
            text,
            reply_markup=select_product_keyboard(slug),
        )

    await callback.answer()


@router.callback_query(OrderStates.waiting_for_product, F.data.startswith("select_product:"))
async def select_product(callback: CallbackQuery, state: FSMContext):
    slug = callback.data.split(":", 1)[1]
    product_row = get_product(slug)
    product_info = PRODUCTS.get(slug)

    if not product_row or not product_info:
        await callback.answer("Маҳсулот топилмади", show_alert=True)
        return

    if product_row["stock"] <= 0:
        await callback.answer("❌ Ушбу маҳсулот тугаган", show_alert=True)
        return

    await state.update_data(
        product_slug=slug,
        product_name=product_info["name"],
    )

    await callback.message.answer(
        "📱 Маҳсулотни қабул қилиб олувчи телефон рақамни киритинг.\n"
        "📌 Намуна: <code>+998901234567</code>"
    )
    await state.set_state(OrderStates.waiting_for_phone)
    await callback.answer()


@router.message(OrderStates.waiting_for_phone)
async def get_phone(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not valid_phone(text):
        await message.answer(
            f"{ERROR_TEXT}\n\n📱 Телефон рақамни тўғри форматда киритинг.\n"
            "📌 Намуна: <code>+998901234567</code>"
        )
        return

    await state.update_data(phone=text)
    await message.answer(
        "🌍 Етказиб бериш давлатини танланг.",
        reply_markup=countries_keyboard(),
    )
    await state.set_state(OrderStates.waiting_for_country)


@router.message(OrderStates.waiting_for_country)
async def get_country(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text not in COUNTRIES:
        await message.answer(
            f"{ERROR_TEXT}\n\n🌍 Қуйидаги тугмалардан бирини танланг.",
            reply_markup=countries_keyboard(),
        )
        return

    await state.update_data(country=text)
    await message.answer(
        "📍 Вилоятигизни танланг.",
        reply_markup=regions_keyboard(text),
    )
    await state.set_state(OrderStates.waiting_for_region)


@router.message(OrderStates.waiting_for_region)
async def get_region(message: Message, state: FSMContext):
    data = await state.get_data()
    country = data.get("country", "")
    available_regions = COUNTRY_REGIONS.get(country, [])
    text = (message.text or "").strip()

    if text not in available_regions:
        await message.answer(
            f"{ERROR_TEXT}\n\n📍 Қуйидаги тугмалардан бирини танланг.",
            reply_markup=regions_keyboard(country),
        )
        return

    await state.update_data(region=text)
    await message.answer(
        "🏠 Аниқ манзилингизни киритинг.\n"
        "📌 Намуна:\n"
        "<code>Тошкент шаҳри, Чилонзор тумани, 19-квартал, 12-уй, 45-хонадон</code>",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(OrderStates.waiting_for_address)


@router.message(OrderStates.waiting_for_address)
async def get_address(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not valid_address(text):
        await message.answer(
            f"{ERROR_TEXT}\n\n🏠 Манзилни тўлиқ кўринишда ёзинг.\n"
            "📌 Намуна:\n"
            "<code>Самарқанд вилояти, Ургут тумани, Мустақиллик кўчаси, 24-уй</code>"
        )
        return

    await state.update_data(address=text)
    data = await state.get_data()

    await message.answer(
        build_review_text(data),
        reply_markup=review_keyboard(),
    )
    await state.set_state(OrderStates.waiting_for_review)


@router.callback_query(OrderStates.waiting_for_review, F.data == "edit_order")
async def edit_order(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.waiting_for_product)

    try:
        await callback.message.delete()
    except Exception:
        pass

    await send_catalog(callback)
    await callback.answer()


@router.callback_query(OrderStates.waiting_for_review, F.data == "cancel_order")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "❌ Буюртма бекор қилинди.",
        reply_markup=start_keyboard()
    )
    await callback.answer()


@router.callback_query(OrderStates.waiting_for_review, F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product_slug = data["product_slug"]

    success = decrease_stock(product_slug, 1)
    if not success:
        await callback.message.answer(
            "❌ Ушбу маҳсулот тугаган. Илтимос, бошқа маҳсулот танланг."
        )
        await state.set_state(OrderStates.waiting_for_product)
        await send_catalog(callback)
        await callback.answer()
        return

    order_id = create_order(
        telegram_user_id=callback.from_user.id,
        telegram_username=callback.from_user.username,
        customer_id_code=data["customer_id_code"],
        full_name=data["full_name"],
        product_slug=data["product_slug"],
        product_name=data["product_name"],
        phone=data["phone"],
        country=data["country"],
        region=data["region"],
        address=data["address"],
    )

    admin_text = build_admin_text(
        order_id,
        callback.from_user.id,
        callback.from_user.username,
        data
    )

for admin_id in config.admin_ids:
    await callback.bot.send_message(
        chat_id=admin_id,
        text=admin_text,
        reply_markup=admin_order_keyboard(order_id),
    )

    await callback.message.answer(
        SUCCESS_TEXT,
        reply_markup=start_keyboard(),
    )
    await state.clear()
    await callback.answer()
