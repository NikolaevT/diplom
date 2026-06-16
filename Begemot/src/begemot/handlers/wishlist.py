from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from src.begemot.config.settings import settings
from src.begemot.repository.employee_repository import EmployeeRepository
from src.begemot.states.forms import Form

router = Router(name="wishlist")


@router.message(Command("get_wishlists"))
async def cmd_get_wishlists(message: types.Message) -> None:
    if message.from_user.id not in settings.admin_id_list:
        await message.answer("Эта команда доступна только администраторам.")
        return

    employees = EmployeeRepository.load_all()
    if not employees:
        await message.answer("Сотрудники не найдены.")
        return

    for employee in employees:
        user_info = f"👤 Пользователь: {employee['name']} (ID: {employee['user_id']})\n"
        items = employee["wishlist_items"]
        items_text = "\n".join(f"• {item}" for item in items)
        if items_text:
            await message.answer(f"{user_info}🎁 Вишлист:\n\n{items_text}")
        else:
            await message.answer(f"{user_info}Вишлист пуст.")


@router.message(lambda message: message.text == "Мой вишлист")
async def handle_wishlist(message: types.Message) -> None:
    builder = ReplyKeyboardBuilder()
    buttons = [
        "Добавить в вишлист",
        "Посмотреть мой вишлист",
        "Удалить из вишлиста",
        "⬅️ Назад",
    ]
    for btn in buttons:
        builder.add(types.KeyboardButton(text=btn))
    builder.adjust(1)

    await message.answer(
        "Управление вашим вишлистом:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )


@router.message(lambda message: message.text == "Посмотреть мой вишлист")
async def view_wishlist(message: types.Message) -> None:
    user_id = message.from_user.id
    items = EmployeeRepository.get_wishlist_items(user_id)
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="⬅️ Назад"))

    if items:
        items_text = "\n".join(f"• {item}" for item in items)
        await message.answer(
            f"🎁 Ваш вишлист:\n\n{items_text}",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    else:
        await message.answer(
            "Ваш вишлист пока пуст. Хотите что-нибудь добавить?",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )


@router.message(lambda message: message.text == "Добавить в вишлист")
async def add_to_wishlist_start(message: types.Message, state: FSMContext) -> None:
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="⬅️ Назад"))
    await message.answer(
        "Что вы хотите добавить в вишлист? Напишите ваш вариант:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )
    await state.set_state(Form.wishlist_item)


@router.message(Form.wishlist_item)
async def add_to_wishlist_finish(message: types.Message, state: FSMContext) -> None:
    if message.text == "⬅️ Назад":
        await state.clear()
        await handle_wishlist(message)
        return

    user_id = message.from_user.id
    items = EmployeeRepository.get_wishlist_items(user_id)
    items.append(message.text)
    EmployeeRepository.save_wishlist_items(user_id, items)

    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="⬅️ Назад"))
    await message.answer(
        "✅ Пункт добавлен в ваш вишлист!",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )
    await state.clear()
    await handle_wishlist(message)


@router.message(lambda message: message.text == "Удалить из вишлиста")
async def remove_from_wishlist_start(message: types.Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    items = EmployeeRepository.get_wishlist_items(user_id)

    if not items:
        builder = ReplyKeyboardBuilder()
        builder.add(types.KeyboardButton(text="⬅️ Назад"))
        await message.answer(
            "Ваш вишлист пуст, нечего удалять.",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
        return

    builder = ReplyKeyboardBuilder()
    for i, item in enumerate(items, 1):
        builder.add(types.KeyboardButton(text=f"{i}. {item}"))
    builder.add(types.KeyboardButton(text="⬅️ Назад"))
    builder.adjust(1)

    await message.answer(
        "Выберите пункт для удаления:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )
    await state.set_state(Form.wishlist_remove)


@router.message(Form.wishlist_remove)
async def remove_from_wishlist_finish(message: types.Message, state: FSMContext) -> None:
    if message.text == "⬅️ Назад":
        await state.clear()
        await handle_wishlist(message)
        return

    user_id = message.from_user.id
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="⬅️ Назад"))

    try:
        item_num = int(message.text.split(".")[0]) - 1
        items = EmployeeRepository.get_wishlist_items(user_id)
        removed_item = items.pop(item_num)
        EmployeeRepository.save_wishlist_items(user_id, items)
        await message.answer(
            f"✅ Пункт '{removed_item}' удален из вишлиста!",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
    except (ValueError, IndexError, KeyError):
        await message.answer(
            "❌ Неверный выбор. Пожалуйста, выберите пункт из списка.",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )

    await state.clear()
    await handle_wishlist(message)
