from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from src.main import app
from src.targeting_service.deps import (
    get_distribution_repository,
    ensure_valid_token,
    ensure_db,
)


def override_ensure_valid_token() -> None:
    return None


def override_ensure_db() -> None:
    return None


app.dependency_overrides[ensure_valid_token] = override_ensure_valid_token
app.dependency_overrides[ensure_db] = override_ensure_db


def test_create_distribution() -> None:
    mock_repo = MagicMock()
    mock_repo.has_linked_recipients.return_value = False
    mock_repo.get_by_bmc_distribution_id.return_value = None

    def override_get_distribution_repository():
        return mock_repo

    app.dependency_overrides[get_distribution_repository] = override_get_distribution_repository

    client = TestClient(app)

    payload = {
        "bmcDistributionId": "ai-777",
        "name": "Ai department",
        "post": {
            "content": "Hello world",
            "imageUrl": None,
            "sourceUrl": None,
        },
    }

    with patch("src.targeting_service.service.distribution_service.db") as mock_db:
        mock_db.atomic.return_value.__enter__.return_value = None
        mock_db.atomic.return_value.__exit__.return_value = False

        response = client.post(
            "/api/v1/distribution",
            json=payload,
            headers={"Authorization": "BAP_Bearer fake-token"},
        )

    assert response.status_code == 422

    mock_repo.create.assert_called_once()
    args, _ = mock_repo.create.call_args
    entity = args[0]
    assert entity.bmc_distribution_id == "ai-777"