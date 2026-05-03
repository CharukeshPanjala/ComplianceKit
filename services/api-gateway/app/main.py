from fastapi import FastAPI
from app.api.v1.router import router
from app.config import settings
from common.log_config import configure_logging, get_logger
from common.middleware.request_logger import LoggingMiddleware

configure_logging(environment=settings.environment)

logger = get_logger(__name__)

app = FastAPI(
    title="API Gateway",
    version="1.0.0",
)

app.add_middleware(LoggingMiddleware)
app.include_router(router)

logger.info("api_gateway_started", environment=settings.environment)