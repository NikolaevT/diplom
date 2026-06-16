from aiogram.types import BufferedInputFile, InlineKeyboardButton, InlineKeyboardMarkup, Message
from loguru import logger

from src.hr.bot_instance import get_bot
from src.hr.dto import AppointmentDto, InstructionDto, OfferDto


class TelegramClient:
    """
    Клиент для отправки сообщений кандидату в Telegram.
    """

    def _build_appointment_keyboard(self, appointment_id: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Согласен",
                        callback_data=f"apt:agree:{appointment_id}",
                    ),
                    InlineKeyboardButton(
                        text="Перенести",
                        callback_data=f"apt:reschedule:{appointment_id}",
                    ),
                    InlineKeyboardButton(
                        text="Отказ",
                        callback_data=f"apt:decline:{appointment_id}",
                    ),
                ]
            ]
        )

    def _format_appointment_message(self, appointment: AppointmentDto) -> str:
        return (
            "<b>Вам назначено собеседование:</b>\n\n"
            f"📅 Дата: {appointment.date}\n"
            f"🕐 Время: {appointment.time}\n"
            f"📍 Место: {appointment.location}"
        )

    async def send_appointment(self, appointment: AppointmentDto) -> int:
        """Отправляет кандидату уведомление о собеседовании с кнопками."""
        bot = get_bot()
        text = self._format_appointment_message(appointment)
        keyboard = self._build_appointment_keyboard(appointment.appointment_id)

        message: Message = await bot.send_message(
            chat_id=appointment.telegram_id,
            text=text,
            reply_markup=keyboard,
        )
        logger.info(
            f"Собеседование отправлено: appointmentId={appointment.appointment_id}, "
            f"telegramId={appointment.telegram_id}, messageId={message.message_id}"
        )
        return message.message_id

    def _build_offer_keyboard(self, offer_id: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Принять",
                        callback_data=f"offer:accept:{offer_id}",
                    ),
                    InlineKeyboardButton(
                        text="Отклонить",
                        callback_data=f"offer:reject:{offer_id}",
                    ),
                ]
            ]
        )

    def _build_documents_keyboard(self, offer_id: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Отправить по почте",
                        callback_data=f"docs:mail:{offer_id}",
                    ),
                    InlineKeyboardButton(
                        text="Передать лично бухгалтеру",
                        callback_data=f"docs:in_person:{offer_id}",
                    ),
                ]
            ]
        )

    async def send_offer(self, offer: OfferDto, file_bytes: bytes) -> int:
        """Отправляет оффер кандидату как документ с кнопками."""
        bot = get_bot()
        document = BufferedInputFile(file=file_bytes, filename=offer.file_name)
        keyboard = self._build_offer_keyboard(offer.offer_id)
        caption = "<b>Вам направлен оффер</b>"

        message: Message = await bot.send_document(
            chat_id=offer.telegram_id,
            document=document,
            caption=caption,
            reply_markup=keyboard,
        )
        logger.info(
            f"Оффер отправлен: offerId={offer.offer_id}, "
            f"telegramId={offer.telegram_id}, messageId={message.message_id}"
        )
        return message.message_id

    async def send_documents_delivery_choice(self, chat_id: str, offer_id: str) -> None:
        """Предлагает кандидату выбрать способ сдачи документов."""
        bot = get_bot()
        keyboard = self._build_documents_keyboard(offer_id)
        await bot.send_message(
            chat_id=chat_id,
            text=(
                "<b>Для оформления необходимо предоставить документы.</b>\n\n"
                "Выберите удобный способ передачи:"
            ),
            reply_markup=keyboard,
        )

    async def send_instruction(self, instruction: InstructionDto, file_bytes: bytes) -> int:
        """Отправляет инструкцию кандидату как документ без кнопок."""
        bot = get_bot()
        document = BufferedInputFile(file=file_bytes, filename=instruction.file_name)
        caption = "<b>Вам направлена инструкция</b>"

        message: Message = await bot.send_document(
            chat_id=instruction.telegram_id,
            document=document,
            caption=caption,
        )
        logger.info(
            f"Инструкция отправлена: instructionId={instruction.instruction_id}, "
            f"telegramId={instruction.telegram_id}, messageId={message.message_id}"
        )
        return message.message_id


telegram_client = TelegramClient()
