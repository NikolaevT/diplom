from datetime import date, datetime

from aiogram import Bot
from loguru import logger
from src.begemot.config.settings import settings
from src.begemot.repository.employee_repository import EmployeeRepository


class ReminderService:
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def send_birthday_reminder(self) -> None:
        admin_ids = settings.admin_id_list
        if not admin_ids:
            return

        today = datetime.now().date()
        employees_data = EmployeeRepository.load_all()
        reminders: list[dict] = []

        for employee in employees_data:
            try:
                day, month = map(int, employee["birthday"].split("."))
                birthday_date = date(today.year, month, day)
                if birthday_date < today:
                    birthday_date = date(today.year + 1, month, day)
                days_left = (birthday_date - today).days
                if days_left == 7:
                    reminders.append(employee)
            except (ValueError, KeyError) as exc:
                logger.warning(f"Ошибка обработки данных сотрудника: {exc}")
                continue

        if not reminders:
            return

        for birthday_employee in reminders:
            birthday_person = birthday_employee["name"]
            message = f"🎉 Через 7 дней у {birthday_person} день рождения!\n"
            message += f"Дата рождения: {birthday_employee['birthday']}\n\n"

            if birthday_employee["wishlist_items"]:
                message += "🎁 Вишлист именинника:\n"
                message += "\n".join(f"• {item}" for item in birthday_employee["wishlist_items"])
            else:
                message += "🎁 Вишлист пока пуст."

            for employee in employees_data:
                emp_user_id = employee["user_id"]
                if emp_user_id != birthday_employee["user_id"]:
                    try:
                        await self._bot.send_message(emp_user_id, message)
                    except Exception as exc:
                        logger.error(
                            f"Ошибка отправки уведомления пользователю {emp_user_id}: {exc}"
                        )

            for admin_id in admin_ids:
                try:
                    await self._bot.send_message(
                        admin_id,
                        f"📢 Отправлено уведомление о ДР {birthday_person}\n\n{message}",
                    )
                except Exception as exc:
                    logger.error(f"Ошибка отправки уведомления admin {admin_id}: {exc}")

    async def send_monthly_birthdays(self) -> None:
        admin_ids = settings.admin_id_list
        if not admin_ids:
            return

        today = datetime.now().date()
        next_month = today.month % 12 + 1
        employees_data = EmployeeRepository.load_all()

        monthly_birthdays = [
            emp
            for emp in employees_data
            if int(emp["birthday"].split(".")[1]) == next_month
        ]

        if not monthly_birthdays:
            return

        message = "🎉 Именинники следующего месяца:\n\n" + "\n".join(
            f"• {emp['birthday']} - {emp['name']}" for emp in monthly_birthdays
        )

        for employee in employees_data:
            try:
                await self._bot.send_message(employee["user_id"], message)
            except Exception as exc:
                logger.error(
                    f"Ошибка отправки уведомления пользователю {employee['user_id']}: {exc}"
                )

        for admin_id in admin_ids:
            try:
                await self._bot.send_message(admin_id, message)
            except Exception as exc:
                logger.error(f"Ошибка отправки уведомления admin {admin_id}: {exc}")
