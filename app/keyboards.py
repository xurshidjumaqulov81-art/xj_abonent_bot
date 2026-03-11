from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


start_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚀 БОШЛАШ")]
    ],
    resize_keyboard=True
)


products_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="XJ EYE CREAM")],
        [KeyboardButton(text="XJ DAY CREAM")],
        [KeyboardButton(text="XJ NIGHT CREAM")],
        [KeyboardButton(text="XJ CLEANSING OIL")],
        [KeyboardButton(text="XJ FACE TONER")],
        [KeyboardButton(text="XJ 24K GOLD SERUM")],
        [KeyboardButton(text="XJ FACE WASH")]
    ],
    resize_keyboard=True
)
