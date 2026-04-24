import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from common.db.session import get_admin_session


@pytest.fixture
def client():
    """FastAPI test client with DB dependency overridden."""
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    async def override_get_admin_session():
        yield mock_session

    app.dependency_overrides[get_admin_session] = override_get_admin_session
    yield TestClient(app), mock_session
    app.dependency_overrides.clear()