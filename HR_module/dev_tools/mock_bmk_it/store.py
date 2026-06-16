"""
In-memory хранилище для локальной разработки mock БМК-ИТ.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Candidate:
    full_name: str
    birth_date: str
    email: str
    telegram_id: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Appointment:
    appointment_id: str
    telegram_id: str
    date: str
    time: str
    location: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Offer:
    offer_id: str
    telegram_id: str
    file_path: str
    file_name: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Instruction:
    instruction_id: str
    telegram_id: str
    file_path: str
    file_name: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class HrNotification:
    event: str
    payload: dict
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


_notifications: list[HrNotification] = []
_candidates: dict[str, Candidate] = {}
_appointments: dict[str, Appointment] = {}
_offers: dict[str, Offer] = {}
_instructions: dict[str, Instruction] = {}


def save_candidate(candidate: Candidate) -> Candidate:
    """Сохраняет кандидата по telegram_id."""
    _candidates[candidate.telegram_id] = candidate
    print(f"[MOCK BMK-IT] Candidate registered: {candidate.telegram_id}")
    return candidate


def get_candidate(telegram_id: str) -> Candidate | None:
    return _candidates.get(telegram_id)


def list_candidates() -> list[Candidate]:
    return list(_candidates.values())


def clear_candidates() -> None:
    _candidates.clear()


def save_appointment(appointment: Appointment) -> Appointment:
    _appointments[appointment.appointment_id] = appointment
    print(f"[MOCK BMK-IT] Appointment scheduled: {appointment.appointment_id}")
    return appointment


def get_appointment(appointment_id: str) -> Appointment | None:
    return _appointments.get(appointment_id)


def list_appointments() -> list[Appointment]:
    return list(_appointments.values())


def clear_appointments() -> None:
    _appointments.clear()


def save_offer(offer: Offer) -> Offer:
    _offers[offer.offer_id] = offer
    print(f"[MOCK BMK-IT] Offer saved: {offer.offer_id}")
    return offer


def get_offer(offer_id: str) -> Offer | None:
    return _offers.get(offer_id)


def list_offers() -> list[Offer]:
    return list(_offers.values())


def clear_offers() -> None:
    _offers.clear()


def save_instruction(instruction: Instruction) -> Instruction:
    _instructions[instruction.instruction_id] = instruction
    print(f"[MOCK BMK-IT] Instruction saved: {instruction.instruction_id}")
    return instruction


def get_instruction(instruction_id: str) -> Instruction | None:
    return _instructions.get(instruction_id)


def list_instructions() -> list[Instruction]:
    return list(_instructions.values())


def clear_instructions() -> None:
    _instructions.clear()


def notify_hr(event: str, payload: dict) -> None:
    """Имитация уведомления HR-специалиста в БМК-ИТ."""
    note = HrNotification(event=event, payload=payload)
    _notifications.append(note)
    print(f"[MOCK BMK-IT → HR] {event}: {payload}")


def list_notifications() -> list[HrNotification]:
    return list(_notifications)


def clear_notifications() -> None:
    _notifications.clear()
