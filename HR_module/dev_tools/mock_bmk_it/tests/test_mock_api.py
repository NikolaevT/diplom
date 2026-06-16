import pytest
from httpx import ASGITransport, AsyncClient

from dev_tools.mock_bmk_it.main import app
from dev_tools.mock_bmk_it.store import (
    clear_appointments,
    clear_candidates,
    clear_instructions,
    clear_notifications,
    clear_offers,
)


@pytest.fixture(autouse=True)
def _clear_store():
    clear_instructions()
    clear_offers()
    clear_appointments()
    clear_candidates()
    clear_notifications()
    yield
    clear_instructions()
    clear_offers()
    clear_appointments()
    clear_candidates()
    clear_notifications()


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_confirm_appointment():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.put(
            "/appointment/confirm",
            json={"appointmentId": "apt-1", "telegramId": "12345"},
        )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.asyncio
async def test_register_candidate():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/candidates",
            json={
                "fullName": "Иван Иванов",
                "birthDate": "17.02.2004",
                "email": "ivan@example.com",
                "telegramId": "12345",
            },
        )
        candidate_resp = await client.get("/candidates/12345")

    assert resp.status_code == 200
    assert resp.json()["telegramId"] == "12345"
    assert candidate_resp.status_code == 200
    assert candidate_resp.json()["email"] == "ivan@example.com"


@pytest.mark.asyncio
async def test_cancel_appointment():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.delete(
            "/appointment",
            params={"appointmentId": "apt-1", "telegramId": "12345"},
        )
    assert resp.status_code == 200
    assert resp.json()["success"] is True


@pytest.mark.asyncio
async def test_schedule_appointment(monkeypatch):
    captured: dict = {}

    async def fake_post(self, url, **kwargs):
        captured["url"] = url
        captured["json"] = kwargs.get("json")

        class FakeResponse:
            status_code = 200

            @staticmethod
            def raise_for_status():
                return None

            @staticmethod
            def json():
                return {"success": True}

        return FakeResponse()

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        post = fake_post

    monkeypatch.setattr(
        "dev_tools.mock_bmk_it.main.httpx.AsyncClient",
        lambda **kwargs: FakeClient(),
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            "/candidates",
            json={
                "fullName": "Иван Иванов",
                "birthDate": "17.02.2004",
                "email": "ivan@example.com",
                "telegramId": "12345",
            },
        )
        resp = await client.post(
            "/appointments",
            json={
                "appointmentId": "apt-1",
                "telegramId": "12345",
                "date": "2026-05-26",
                "time": "14:00",
                "location": "Офис, ул. Примерная 1",
            },
        )

    assert resp.status_code == 200
    assert resp.json()["appointmentId"] == "apt-1"
    assert captured["json"]["telegramId"] == "12345"


@pytest.mark.asyncio
async def test_schedule_appointment_unknown_candidate():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/appointments",
            json={
                "appointmentId": "apt-1",
                "telegramId": "99999",
                "date": "2026-05-26",
                "time": "14:00",
                "location": "Офис",
            },
        )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_send_offer(monkeypatch, tmp_path):
    captured: dict = {}

    async def fake_post(self, url, **kwargs):
        captured["url"] = url
        captured["json"] = kwargs.get("json")

        class FakeResponse:
            status_code = 200

            @staticmethod
            def raise_for_status():
                return None

        return FakeResponse()

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        post = fake_post

    monkeypatch.setattr(
        "dev_tools.mock_bmk_it.main.httpx.AsyncClient",
        lambda **kwargs: FakeClient(),
    )
    monkeypatch.setattr("dev_tools.mock_bmk_it.main.FILES_DIR", tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            "/candidates",
            json={
                "fullName": "Иван Иванов",
                "birthDate": "17.02.2004",
                "email": "ivan@example.com",
                "telegramId": "12345",
            },
        )
        files = {"file": ("Offer.pdf", b"%PDF-1.4 fake", "application/pdf")}
        resp = await client.post(
            "/offers",
            data={"offerId": "offer-1", "telegramId": "12345"},
            files=files,
        )
        file_resp = await client.get("/offers/offer-1/file")

    assert resp.status_code == 200
    assert resp.json()["offerId"] == "offer-1"
    assert captured["json"]["telegramId"] == "12345"
    assert file_resp.status_code == 200


@pytest.mark.asyncio
async def test_send_instruction(monkeypatch, tmp_path):
    captured: dict = {}

    async def fake_post(self, url, **kwargs):
        captured["json"] = kwargs.get("json")

        class FakeResponse:
            status_code = 200

            @staticmethod
            def raise_for_status():
                return None

        return FakeResponse()

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        post = fake_post

    monkeypatch.setattr(
        "dev_tools.mock_bmk_it.main.httpx.AsyncClient",
        lambda **kwargs: FakeClient(),
    )
    monkeypatch.setattr("dev_tools.mock_bmk_it.main.FILES_DIR", tmp_path)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.post(
            "/candidates",
            json={
                "fullName": "Иван Иванов",
                "birthDate": "17.02.2004",
                "email": "ivan@example.com",
                "telegramId": "12345",
            },
        )
        files = {"file": ("Instruction.pdf", b"%PDF-1.4 fake", "application/pdf")}
        resp = await client.post(
            "/instructions",
            data={"instructionId": "instr-1", "telegramId": "12345"},
            files=files,
        )
        file_resp = await client.get("/instructions/instr-1/file")

    assert resp.status_code == 200
    assert resp.json()["instructionId"] == "instr-1"
    assert captured["json"]["telegramId"] == "12345"
    assert file_resp.status_code == 200
