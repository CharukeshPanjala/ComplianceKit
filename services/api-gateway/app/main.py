from fastapi import FastAPI
from app.api.v1.router import router
from app.config import settings
from common.log_config import configure_logging, get_logger
from common.middleware.request_logger import LoggingMiddleware
from common.tracing import configure_tracing
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from common.db.session import engine

configure_logging(environment=settings.environment)
configure_tracing(service_name="api-gateway", environment=settings.environment)

logger = get_logger(__name__)

app = FastAPI(
    title="API Gateway",
    version="1.0.0",
)

FastAPIInstrumentor.instrument_app(app)
SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)

app.add_middleware(LoggingMiddleware)
app.include_router(router)

logger.info("api_gateway_started", environment=settings.environment)