import os
import logging
from sqlmodel import SQLModel
from fastapi import FastAPI, Request
import time
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
    """Log the method, path, status code, and duration of every HTTP request."""
    start = time.perf_counter()
    response = await call_next(request)
    duration = (time.perf_counter() - start) * 1000
    logger.info(f"{request.method} {request.url.path} - {response.status_code} ({duration:.1f}ms)")
    return response
