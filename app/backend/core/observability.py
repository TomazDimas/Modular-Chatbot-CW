import time, uuid, structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

log = structlog.get_logger()

class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("x-request-id") or str(uuid.uuid4())
        t0 = time.time()
        try:
            response: Response = await call_next(request)
            ms = int((time.time() - t0) * 1000)
            log.bind(level="INFO", agent="API", path=request.url.path, method=request.method,
                     status=response.status_code, request_id=rid, execution_time_ms=ms).msg("http_request_done")
            response.headers["x-request-id"] = rid
            return response
        except Exception as e:
            ms = int((time.time() - t0) * 1000)
            log.bind(level="ERROR", agent="API", path=request.url.path, method=request.method,
                     request_id=rid, execution_time_ms=ms, error=str(e)).msg("http_request_failed")
            raise
