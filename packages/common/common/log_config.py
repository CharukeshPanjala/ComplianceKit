import logging
import sys
import structlog
from structlog.types import Processor


def configure_logging(environment: str = "development") -> None:
    shared_processors: list[Processor] = [
    structlog.contextvars.merge_contextvars,
    structlog.stdlib.add_logger_name,
    structlog.stdlib.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.StackInfoRenderer(),
]

    if environment == "production":
        processors = shared_processors + [
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # configure stdlib logging to not duplicate output
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    return structlog.get_logger(name)