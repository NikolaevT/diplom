import aiohttp
from loguru import logger

from src.newspaper.config import settings


class RecipientClient:
    """Клиент для регистрации получателей через внешний API."""

    @staticmethod
    async def register(
        telegram_id: int,
        name: str,
        recipient_type: str,
        is_admin: bool = False,
    ) -> bool:
        """
        Отправляет POST-запрос на внешний сервис для регистрации получателя.

        Args:
            telegram_id: Telegram ID пользователя или чата
            name: Имя пользователя или название чата
            recipient_type: Тип получателя (private, group, supergroup, channel)
            is_admin: Является ли получатель администратором

        Returns:
            True если регистрация прошла успешно, False в случае ошибки
        """
        payload = {
            "telegramId": str(telegram_id),
            "name": name,
            "type": recipient_type,
            "isAdmin": is_admin,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.recipient_api_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status in (200, 201):
                        logger.info(
                            f"Получатель зарегистрирован: "
                            f"telegramId={telegram_id}, name='{name}', type={recipient_type}"
                        )
                        return True

                    body = await resp.text()
                    logger.error(
                        f"Ошибка регистрации получателя: " f"status={resp.status}, body={body}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Ошибка при вызове API регистрации получателя: {e}")
            return False
