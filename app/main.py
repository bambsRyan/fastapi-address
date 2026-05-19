import os
import logging
import time

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel

from .database import engine
from .api.v1.router import router as api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

os.makedirs("data", exist_ok=True)
SQLModel.metadata.create_all(engine)
logger.info("Database tables created")

app = FastAPI(title="Address Book API")

app.include_router(api_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log every request. Catches unhandled exceptions so internals are never leaked."""
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.error(f"Unhandled error on {request.method} {request.url.path}", exc_info=exc)
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})
    duration = (time.perf_counter() - start) * 1000
    logger.info(f"{request.method} {request.url.path} - {response.status_code} ({duration:.1f}ms)")
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Log expected HTTP errors (4xx/5xx) and return the standard error response."""
    logger.warning(f"{request.method} {request.url.path} - {exc.status_code}: {exc.detail}")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
