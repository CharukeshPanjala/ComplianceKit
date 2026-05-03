import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from common.log_config import configure_logging, get_logger
from common.middleware.request_logger import LoggingMiddleware


@pytest.fixture
def app():
    configure_logging(environment="development")
    test_app = FastAPI()
    test_app.add_middleware(LoggingMiddleware)

    @test_app.get("/test")
    async def test_route():
        return {"status": "ok"}

    return test_app


@pytest.fixture
def client(app):
    return TestClient(app)


class TestLogging:

    def test_request_id_in_response_header(self, client):
        """Every response must have X-Request-ID header."""
        response = client.get("/test")
        assert "x-request-id" in response.headers
        assert len(response.headers["x-request-id"]) > 0

    def test_request_id_is_unique_per_request(self, client):
        """Each request gets a different request_id."""
        response1 = client.get("/test")
        response2 = client.get("/test")
        assert response1.headers["x-request-id"] != response2.headers["x-request-id"]

    def test_request_id_is_valid_uuid(self, client):
        """request_id must be a valid UUID."""
        import uuid
        response = client.get("/test")
        request_id = response.headers["x-request-id"]
        uuid.UUID(request_id)  # raises ValueError if invalid

    def test_configure_logging_development(self):
        """configure_logging runs without errors in development mode."""
        configure_logging(environment="development")

    def test_configure_logging_production(self):
        """configure_logging runs without errors in production mode."""
        configure_logging(environment="production")

    def test_get_logger_returns_logger(self):
        """get_logger returns a structlog logger."""
        logger = get_logger("test")
        assert logger is not None