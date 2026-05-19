from fastapi import APIRouter

from app.api.v1.endpoints import addresses

router = APIRouter(prefix="/api/v1")

router.include_router(addresses.router)
