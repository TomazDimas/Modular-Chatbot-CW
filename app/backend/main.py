from __future__ import annotations
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse

from .core.config import settings
from .core.logging_conf import setup_logging
from .core.errors import unhandled_exception_handler
from .core.observability import RequestLogMiddleware
from .api.router import router as api_router

def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(title=settings.app_name)

    app.add_exception_handler(Exception, unhandled_exception_handler)
    app.add_exception_handler(StarletteHTTPException, unhandled_exception_handler)  
    app.add_middleware(RequestLogMiddleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app

app = create_app()
