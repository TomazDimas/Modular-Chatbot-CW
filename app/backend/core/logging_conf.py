
from __future__ import annotations
import logging
import structlog
import os

LOG_FORMAT = os.getenv("LOG_FORMAT", "pretty").lower()

def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level)

    processors = [
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if LOG_FORMAT == "json":
        processors.append(structlog.dev.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )
