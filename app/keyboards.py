from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from app.texts import COUNTRIES, COUNTRY_REGIONS


def start_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🚀 БОШЛАШ")],
        ],
        resize_keyboard=True,
    )


def countries_keyboard() -> ReplyKeyboardMarkup:
    rows = [[KeyboardButton(text=country)] for country in COUNTRIES]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def regions_keyboard(country: str) -> ReplyKeyboardMarkup:
    regions = COUNTRY_REGIONS.get(country, [])
    rows = [[KeyboardButton(text=region)] for region in regions]
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def products_keyboard(products: list[dict]) -> InlineKeyboardMarkup:
    buttons = []
    for product in products:
        text = f"{product['name']} — ҚОЛДИ {product['stock']} ТА"
        buttons.append(
            [InlineKeyboardButton(
                text=text,
                callback_data=f"view_product:{product['slug']}"
            )]
        )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def select_product_keyboard(slug: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ ТАНЛАШ", callback_data=f"select_product:{slug}")],
            [InlineKeyboardButton(text="⬅️ КАТАЛОГГА ҚАЙТИШ", callback_data="back_to_catalog")],
        ]
    )


def review_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ ТАСДИҚЛАШ", callback_data="confirm_order")],
            [InlineKeyboardButton(text="✏️ ТАҲРИРЛАШ", callback_data="edit_order")],
            [InlineKeyboardButton(text="❌ БЕКОР ҚИЛИШ", callback_data="cancel_order")],
        ]
    )


def admin_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ ТАСДИҚЛАШ", callback_data=f"admin:approve:{order_id}")],
            [InlineKeyboardButton(text="📞 БОҒЛАНИЛДИ", callback_data=f"admin:contacted:{order_id}")],
            [InlineKeyboardButton(text="🚚 ЮБОРИЛДИ", callback_data=f"admin:shipped:{order_id}")],
            [InlineKeyboardButton(text="❌ БЕКОР ҚИЛИШ", callback_data=f"admin:cancel:{order_id}")],
        ]
    )
