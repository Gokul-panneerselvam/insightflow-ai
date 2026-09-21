"""API v1 master router."""

from fastapi import APIRouter

from src.app.api.v1.endpoints import health

api_router = APIRouter()

# Register health check endpoints
api_router.include_router(health.router, tags=["Health"])
