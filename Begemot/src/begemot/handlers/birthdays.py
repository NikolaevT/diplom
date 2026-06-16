from aiogram import Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.begemot.config.settings import settings
from src.begemot.repository.employee_repository import EmployeeRepository

router = Router(name="birthdays")

MONTH_NAMES = [
    "Января",
    "Февраля",
    "Марта",
    "Апреля",
    "Мая",
    "Июня",
    "Июля",
    "Августа",
    "Сентября",
    "Октября",
    "Ноября",
    "Декабря",
]

MONTHS = [
    ("Январь", "1"),
    ("Февраль", "2"),
    ("Март", "3"),
    ("Апрель", "4"),
    ("Май", "5"),
    ("Июнь", "6"),
    ("Июль", "7"),
    ("Август", "8"),
    ("Сентябрь", "9"),
    ("Октябрь", "10"),
    ("Ноябрь", "11"),
    ("Декабрь", "12"),
]


def build_month_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for name, num in MONTHS:
        builder.button(text=name, callback_data=f"month_{num}")
    builder.adjust(3)
    return builder.as_markup()


@router.message(lambda message: message.text == "Именинники месяца")
async def show_month_selector(message: types.Message) -> None:
    await message.answer("Выберите месяц:", reply_markup=build_month_keyboard())


@router.callback_query(lambda c: c.data.startswith("month_"))
async def show_month_birthdays(callback: types.CallbackQuery) -> None:
    if callback.data == "month_back":
        await callback.message.edit_text(
            "Выберите месяц:",
            reply_markup=build_month_keyboard(),
        )
        await callback.answer()
        return

    month_num = callback.data.split("_")[1]
    month_name = MONTH_NAMES[int(month_num) - 1]

    birthdays_data = EmployeeRepository.load_birthdays()
    birthdays = sorted(
        [
            emp
            for emp in birthdays_data
            if emp["birthday"].split(".")[1] == month_num.zfill(2)
        ],
        key=lambda x: int(x["birthday"].split(".")[0]),
    )

    is_admin = (
        callback.from_user is not None
        and callback.from_user.id in settings.admin_id_list
    )

    if birthdays:
        text = f"🎉 Именинники {month_name}:\n\n" + "\n".join(
            f"• {emp['birthday']} - {emp['name']}" for emp in birthdays
        )
        if is_admin:
            for emp in birthdays:
                if emp["wishlist_items"]:
                    text += f"\n\n🎁 Вишлист {emp['name']}:\n"
                    text += "\n".join(f"• {item}" for item in emp["wishlist_items"])
    else:
        text = f"В {month_name} нет именинников."

    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="month_back")
    await callback.message.edit_text(text, reply_markup=builder.as_markup())
    await callback.answer()
