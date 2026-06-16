from fastapi.testclient import TestClient
from unittest.mock import patch

from src.main import app
from src.targeting_service.deps import ensure_db
from src.targeting_service.dto.recipient_dto import RecipientDto


def override_ensure_db() -> None:
    return None


app.dependency_overrides[ensure_db] = override_ensure_db


def test_add_recipient() -> None:
    client = TestClient(app)
    payload = {
        "telegramId": "12345",
        "type": "user",
        "name": "test",
        "isAdmin": False,
    }

    expected = RecipientDto(
        telegram_id="12345",
        name="test",
        type="user",
        is_admin=False,
    )

    with patch(
        "src.targeting_service.controller.recipient_controller.create_or_update_recipient"
    ) as mock_create:
        mock_create.return_value = expected

        response = client.post(
            "/api/v1/recipients",
            json=payload,
            
        )

    assert response.status_code == 200
    assert response.json()["telegramId"] == "12345"
    mock_create.assert_called_once()
    call_payload = mock_create.call_args[0][0]
    assert call_payload.telegram_id == "12345"
    assert call_payload.type == "user"
    assert call_payload.name == "test"
    assert call_payload.is_admin is False
