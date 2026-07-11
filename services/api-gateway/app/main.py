from fastapi import FastAPI
from app.api.v1.router import router
from app.config import settings
from common.log_config import configure_logging, get_logger
from common.middleware.request_logger import LoggingMiddleware
from common.tracing import configure_tracing
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from common.db.session import admin_engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from common.middleware.security_headers import SecurityHeadersMiddleware

configure_logging(environment=settings.environment)
configure_tracing(service_name="api-gateway", environment=settings.environment)

logger = get_logger(__name__)

app = FastAPI(
    title="API Gateway",
    version="1.0.0",
)

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

FastAPIInstrumentor.instrument_app(app)
SQLAlchemyInstrumentor().instrument(engine=admin_engine.sync_engine)

app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)
app.include_router(router)

logger.info("api_gateway_started", environment=settings.environment)