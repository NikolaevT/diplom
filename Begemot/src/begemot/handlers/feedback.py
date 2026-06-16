from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from src.begemot.bot_instance import get_bot
from src.begemot.config.settings import settings
from src.begemot.handlers.menu import show_main_menu
from src.begemot.states.forms import Form

router = Router(name="feedback")


@router.message(lambda message: message.text == "Обратная связь")
async def start_feedback(message: types.Message, state: FSMContext) -> None:
    await message.answer("Напишите ваше сообщение (текст, фото или документ):")
    await state.set_state(Form.feedback)


@router.message(Form.feedback)
async def process_feedback(message: types.Message, state: FSMContext) -> None:
    admin_ids = settings.admin_id_list
    bot = get_bot()

    if admin_ids:
        user_info = f"От: {message.from_user.full_name} (ID: {message.from_user.id})\n"

        if message.text:
            for admin_id in admin_ids:
                await bot.send_message(admin_id, user_info + f"Сообщение:\n{message.text}")
        elif message.photo:
            for admin_id in admin_ids:
                await bot.send_photo(
                    admin_id,
                    message.photo[-1].file_id,
                    caption=user_info + (message.caption or ""),
                )
        elif message.document:
            for admin_id in admin_ids:
                await bot.send_document(
                    admin_id,
                    message.document.file_id,
                    caption=user_info + (message.caption or ""),
                )
        else:
            for admin_id in admin_ids:
                await bot.send_message(
                    admin_id,
                    user_info + "Прислан неподдерживаемый тип сообщения",
                )

    await message.answer("✅ Спасибо за обратную связь!")
    await state.clear()
    await show_main_menu(message)
