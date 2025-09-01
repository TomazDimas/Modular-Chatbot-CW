from fastapi import Request
from fastapi.responses import JSONResponse
import structlog

log = structlog.get_logger()

async def unhandled_exception_handler(request: Request, exc: Exception):
    log.bind(level="ERROR", agent="API", path=str(request.url), error=str(exc)).msg("unhandled_error")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
