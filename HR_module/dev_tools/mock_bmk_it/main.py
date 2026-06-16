"""
Mock BMK-IT Service для локальной разработки HR middleware.

Эндпоинты, которые вызывает middleware после действий кандидата в Telegram:
- PUT  /appointment/confirm
- POST /appointment/reschedule
- DELETE /appointment
- PUT  /offer/accept
- PUT  /offer/reject

Запуск локально:
    make mock-bmk

Docker:
    make up
"""

from __future__ import annotations

import inspect
import os
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse

from dev_tools.mock_bmk_it.config import FILES_DIR, MIDDLEWARE_HOST, MOCK_PUBLIC_URL
from dev_tools.mock_bmk_it.dto import (
    ActionResponse,
    AppointmentActionRequest,
    AppointmentRescheduleRequest,
    CandidateRequest,
    CandidateResponse,
    InstructionNotifyRequest,
    InstructionResponse,
    OfferActionRequest,
    OfferNotifyRequest,
    OfferResponse,
    ScheduleAppointmentRequest,
    ScheduleAppointmentResponse,
)
from dev_tools.mock_bmk_it.store import (
    Appointment,
    Candidate,
    Instruction,
    Offer,
    clear_appointments,
    clear_candidates,
    clear_instructions,
    clear_notifications,
    clear_offers,
    get_candidate,
    get_instruction,
    get_offer,
    list_appointments,
    list_candidates,
    list_instructions,
    list_notifications,
    list_offers,
    notify_hr,
    save_appointment,
    save_candidate,
    save_instruction,
    save_offer,
)

MOCK_PORT = int(os.getenv("MOCK_PORT", "8088"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    cat = inspect.cleandoc(
        r"""
          |\      _,,,---,,_
    ZZZzz /,`.-'`'    -.  ;-;;,_
         |,4-  ) )-,_. ,\ (  `'-'
        '---''(_/--'  `-'\_)
      """
    )
    print("\n" + cat + "\n")
    print("Mock BMK-IT Service is running...")
    print(f"Swagger: http://localhost:{MOCK_PORT}/docs")
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="Mock BMK-IT Service",
    description="Имитация БМК-ИТ для HR recruitment flow",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Mock BMK-IT Service is running",
        "docs": f"http://localhost:{MOCK_PORT}/docs",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/debug/notifications")
async def debug_notifications() -> list[dict]:
    """Список имитированных уведомлений HR (только для разработки)."""
    return [
        {
            "event": n.event,
            "payload": n.payload,
            "createdAt": n.created_at.isoformat(),
        }
        for n in list_notifications()
    ]


@app.delete("/debug/notifications", include_in_schema=False)
async def debug_clear_notifications() -> dict[str, str]:
    clear_notifications()
    return {"status": "cleared"}


@app.post("/candidates", response_model=CandidateResponse)
async def register_candidate(body: CandidateRequest) -> CandidateResponse:
    """Сохраняет кандидата, который прошел регистрацию в Telegram-боте."""
    candidate = save_candidate(
        Candidate(
            full_name=body.full_name,
            birth_date=body.birth_date,
            email=body.email,
            telegram_id=body.telegram_id,
        )
    )
    notify_hr("candidate_registered", body.model_dump(by_alias=True))
    return CandidateResponse(
        fullName=candidate.full_name,
        birthDate=candidate.birth_date,
        email=candidate.email,
        telegramId=candidate.telegram_id,
    )


@app.get("/candidates/{telegram_id}", response_model=CandidateResponse | None)
async def read_candidate(telegram_id: str) -> CandidateResponse | None:
    """Возвращает кандидата по telegramId, если он уже зарегистрирован."""
    candidate = get_candidate(telegram_id)
    if candidate is None:
        return None
    return CandidateResponse(
        fullName=candidate.full_name,
        birthDate=candidate.birth_date,
        email=candidate.email,
        telegramId=candidate.telegram_id,
    )


@app.get("/debug/candidates")
async def debug_candidates() -> list[dict]:
    """Список зарегистрированных кандидатов (только для разработки)."""
    return [
        {
            "fullName": c.full_name,
            "birthDate": c.birth_date,
            "email": c.email,
            "telegramId": c.telegram_id,
            "createdAt": c.created_at.isoformat(),
        }
        for c in list_candidates()
    ]


@app.delete("/debug/candidates", include_in_schema=False)
async def debug_clear_candidates() -> dict[str, str]:
    clear_candidates()
    return {"status": "cleared"}


@app.post("/appointments", response_model=ScheduleAppointmentResponse)
async def schedule_appointment(body: ScheduleAppointmentRequest) -> ScheduleAppointmentResponse:
    """
    HR назначает собеседование кандидату.
    Сохраняет в mock и передаёт данные в HR middleware для отправки в Telegram.
    """
    candidate = get_candidate(body.telegram_id)
    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail=f"Candidate with telegramId={body.telegram_id} not found",
        )

    appointment = save_appointment(
        Appointment(
            appointment_id=body.appointment_id,
            telegram_id=body.telegram_id,
            date=body.date,
            time=body.time,
            location=body.location,
        )
    )

    payload = body.model_dump(by_alias=True)
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
        try:
            resp = await client.post(
                f"{MIDDLEWARE_HOST}/api/v1/appointments",
                json=payload,
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Middleware error: {e.response.status_code} {e.response.text}",
            ) from e
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Cannot reach middleware at {MIDDLEWARE_HOST}: {e!r}",
            ) from e

    notify_hr("appointment_scheduled", payload)
    return ScheduleAppointmentResponse(
        appointmentId=appointment.appointment_id,
        telegramId=appointment.telegram_id,
        date=appointment.date,
        time=appointment.time,
        location=appointment.location,
    )


@app.get("/debug/appointments")
async def debug_appointments() -> list[dict]:
    """Список назначенных собеседований (только для разработки)."""
    return [
        {
            "appointmentId": a.appointment_id,
            "telegramId": a.telegram_id,
            "date": a.date,
            "time": a.time,
            "location": a.location,
            "createdAt": a.created_at.isoformat(),
        }
        for a in list_appointments()
    ]


@app.delete("/debug/appointments", include_in_schema=False)
async def debug_clear_appointments() -> dict[str, str]:
    clear_appointments()
    return {"status": "cleared"}


@app.post("/offers", response_model=OfferResponse)
async def send_offer(
    offer_id: str = Form(..., alias="offerId"),
    telegram_id: str = Form(..., alias="telegramId"),
    file: UploadFile = File(...),
) -> OfferResponse:
    """
    HR отправляет оффер кандидату.
    Файл сохраняется в mock и передаётся в middleware для отправки в Telegram.
    """
    candidate = get_candidate(telegram_id)
    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail=f"Candidate with telegramId={telegram_id} not found",
        )

    file_name = file.filename or "Offer.pdf"
    suffix = Path(file_name).suffix or ".pdf"
    file_path = FILES_DIR / f"{offer_id}{suffix}"
    content = await file.read()
    file_path.write_bytes(content)

    save_offer(
        Offer(
            offer_id=offer_id,
            telegram_id=telegram_id,
            file_path=str(file_path),
            file_name=file_name,
        )
    )

    payload = OfferNotifyRequest(
        offerId=offer_id,
        telegramId=telegram_id,
        fileUrl=f"{MOCK_PUBLIC_URL}/offers/{offer_id}/file",
        fileName=file_name,
    )
    notify_payload = payload.model_dump(by_alias=True)

    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        try:
            resp = await client.post(
                f"{MIDDLEWARE_HOST}/api/v1/offers",
                json=notify_payload,
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Middleware error: {e.response.status_code} {e.response.text}",
            ) from e
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Cannot reach middleware at {MIDDLEWARE_HOST}: {e!r}",
            ) from e

    notify_hr("offer_sent", notify_payload)
    return OfferResponse(**notify_payload)


@app.get("/offers/{offer_id}/file")
async def download_offer_file(offer_id: str):
    """Отдаёт файл оффера для скачивания middleware."""
    offer = get_offer(offer_id)
    if offer is None:
        raise HTTPException(status_code=404, detail="Offer not found")

    path = Path(offer.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Offer file not found")

    return FileResponse(path, filename=offer.file_name, media_type="application/pdf")


@app.get("/debug/offers")
async def debug_offers() -> list[dict]:
    """Список отправленных офферов (только для разработки)."""
    return [
        {
            "offerId": o.offer_id,
            "telegramId": o.telegram_id,
            "fileName": o.file_name,
            "filePath": o.file_path,
            "createdAt": o.created_at.isoformat(),
        }
        for o in list_offers()
    ]


@app.delete("/debug/offers", include_in_schema=False)
async def debug_clear_offers() -> dict[str, str]:
    clear_offers()
    return {"status": "cleared"}


@app.post("/instructions", response_model=InstructionResponse)
async def send_instruction(
    instruction_id: str = Form(..., alias="instructionId"),
    telegram_id: str = Form(..., alias="telegramId"),
    file: UploadFile = File(...),
) -> InstructionResponse:
    """
    HR отправляет инструкцию кандидату.
    Файл сохраняется в mock и передаётся в middleware для отправки в Telegram.
    """
    candidate = get_candidate(telegram_id)
    if candidate is None:
        raise HTTPException(
            status_code=404,
            detail=f"Candidate with telegramId={telegram_id} not found",
        )

    file_name = file.filename or "Instruction.pdf"
    suffix = Path(file_name).suffix or ".pdf"
    file_path = FILES_DIR / f"instruction_{instruction_id}{suffix}"
    content = await file.read()
    file_path.write_bytes(content)

    save_instruction(
        Instruction(
            instruction_id=instruction_id,
            telegram_id=telegram_id,
            file_path=str(file_path),
            file_name=file_name,
        )
    )

    payload = InstructionNotifyRequest(
        instructionId=instruction_id,
        telegramId=telegram_id,
        fileUrl=f"{MOCK_PUBLIC_URL}/instructions/{instruction_id}/file",
        fileName=file_name,
    )
    notify_payload = payload.model_dump(by_alias=True)

    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        try:
            resp = await client.post(
                f"{MIDDLEWARE_HOST}/api/v1/instructions",
                json=notify_payload,
            )
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Middleware error: {e.response.status_code} {e.response.text}",
            ) from e
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Cannot reach middleware at {MIDDLEWARE_HOST}: {e!r}",
            ) from e

    notify_hr("instruction_sent", notify_payload)
    return InstructionResponse(**notify_payload)


@app.get("/instructions/{instruction_id}/file")
async def download_instruction_file(instruction_id: str):
    """Отдаёт файл инструкции для скачивания middleware."""
    instruction = get_instruction(instruction_id)
    if instruction is None:
        raise HTTPException(status_code=404, detail="Instruction not found")

    path = Path(instruction.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Instruction file not found")

    return FileResponse(path, filename=instruction.file_name, media_type="application/pdf")


@app.get("/debug/instructions")
async def debug_instructions() -> list[dict]:
    """Список отправленных инструкций (только для разработки)."""
    return [
        {
            "instructionId": i.instruction_id,
            "telegramId": i.telegram_id,
            "fileName": i.file_name,
            "filePath": i.file_path,
            "createdAt": i.created_at.isoformat(),
        }
        for i in list_instructions()
    ]


@app.delete("/debug/instructions", include_in_schema=False)
async def debug_clear_instructions() -> dict[str, str]:
    clear_instructions()
    return {"status": "cleared"}


@app.put("/appointment/confirm", response_model=ActionResponse)
async def confirm_appointment(body: AppointmentActionRequest) -> ActionResponse:
    notify_hr(
        "appointment_confirmed",
        body.model_dump(by_alias=True),
    )
    return ActionResponse(message="Собеседование подтверждено, HR уведомлён")


@app.post("/appointment/reschedule", response_model=ActionResponse)
async def reschedule_appointment(body: AppointmentRescheduleRequest) -> ActionResponse:
    notify_hr(
        "appointment_rescheduled",
        body.model_dump(by_alias=True),
    )
    return ActionResponse(message="Запрос на перенос отправлен HR")


@app.delete("/appointment", response_model=ActionResponse)
async def cancel_appointment(
    appointment_id: str = Query(..., alias="appointmentId"),
    telegram_id: str = Query(..., alias="telegramId"),
) -> ActionResponse:
    payload = {"appointmentId": appointment_id, "telegramId": telegram_id}
    notify_hr("appointment_declined", payload)
    return ActionResponse(message="Собеседование отменено, HR уведомлён")


@app.put("/offer/accept", response_model=ActionResponse)
async def accept_offer(body: OfferActionRequest) -> ActionResponse:
    notify_hr("offer_accepted", body.model_dump(by_alias=True))
    return ActionResponse(message="Оффер принят, HR уведомлён")


@app.put("/offer/reject", response_model=ActionResponse)
async def reject_offer(body: OfferActionRequest) -> ActionResponse:
    notify_hr("offer_rejected", body.model_dump(by_alias=True))
    return ActionResponse(message="Оффер отклонён, HR уведомлён")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=MOCK_PORT)
