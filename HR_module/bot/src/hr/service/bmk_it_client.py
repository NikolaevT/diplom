import httpx
from loguru import logger

from src.hr.config import settings
from src.hr.dto import (
    AppointmentActionDto,
    AppointmentRescheduleDto,
    CandidateDto,
    OfferActionDto,
)


class BmkItClient:
    """
    Клиент для взаимодействия с mock БМК-ИТ.
    """

    def __init__(self) -> None:
        self.base_url = settings.bmk_it_host.rstrip("/")

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=httpx.Timeout(10.0)) as client:
            try:
                resp = await client.request(method, url, **kwargs)
                resp.raise_for_status()
                return resp
            except httpx.HTTPStatusError as e:
                logger.error(
                    f"HTTP ошибка БМК-ИТ {method} {url}: "
                    f"status={e.response.status_code}, body={e.response.text!r}"
                )
                raise
            except httpx.RequestError as e:
                logger.error(f"Ошибка соединения с mock БМК-ИТ: {e!r}")
                raise

    async def get_candidate(self, telegram_id: str) -> CandidateDto | None:
        """Проверяет, зарегистрирован ли кандидат в БМК-ИТ."""
        resp = await self._request("GET", f"/candidates/{telegram_id}")
        data = resp.json()
        if data is None:
            return None
        return CandidateDto(**data)

    async def register_candidate(self, candidate: CandidateDto) -> CandidateDto:
        """Регистрирует кандидата в БМК-ИТ."""
        body = candidate.model_dump(by_alias=True, mode="json")
        resp = await self._request("POST", "/candidates", json=body)
        return CandidateDto(**resp.json())

    async def confirm_appointment(self, action: AppointmentActionDto) -> None:
        """Подтверждает собеседование."""
        body = action.model_dump(by_alias=True, mode="json")
        await self._request("PUT", "/appointment/confirm", json=body)

    async def reschedule_appointment(self, payload: AppointmentRescheduleDto) -> None:
        """Отправляет запрос на перенос собеседования."""
        body = payload.model_dump(by_alias=True, mode="json")
        await self._request("POST", "/appointment/reschedule", json=body)

    async def cancel_appointment(self, action: AppointmentActionDto) -> None:
        """Отменяет собеседование."""
        params = action.model_dump(by_alias=True, mode="json")
        await self._request("DELETE", "/appointment", params=params)

    async def accept_offer(self, action: OfferActionDto) -> None:
        """Фиксирует принятие оффера."""
        body = action.model_dump(by_alias=True, mode="json")
        await self._request("PUT", "/offer/accept", json=body)

    async def reject_offer(self, action: OfferActionDto) -> None:
        """Фиксирует отклонение оффера."""
        body = action.model_dump(by_alias=True, mode="json")
        await self._request("PUT", "/offer/reject", json=body)


bmk_it_client = BmkItClient()
