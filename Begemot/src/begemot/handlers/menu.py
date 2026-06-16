from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def show_main_menu(message: types.Message) -> None:
    builder = ReplyKeyboardBuilder()
    buttons = [
        "О компании",
        "Именинники месяца",
        "Обратная связь",
        "Мой вишлист",
    ]
    for btn in buttons:
        builder.add(types.KeyboardButton(text=btn))
    builder.adjust(2)

    await message.answer(
        "Выберите функцию:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )
