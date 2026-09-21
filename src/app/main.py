"""Main FastAPI application entry point for Insightflow AI."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from src.app.api.v1.router import api_router
from src.app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("insightflow.api")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    logger.info(
        "Starting up %s v%s in %s mode...",
        settings.PROJECT_NAME,
        settings.VERSION,
        settings.ENVIRONMENT,
    )
    yield
    logger.info("Shutting down %s...", settings.PROJECT_NAME)


def create_application() -> FastAPI:
    """Factory to create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS middleware
    origins = ["*"] if settings.ALLOW_ALL_ORIGINS else settings.CORS_ORIGINS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Root endpoint
    @application.get(
        "/",
        status_code=status.HTTP_200_OK,
        summary="Service Root Overview",
        tags=["General"],
    )
    async def root() -> dict[str, str]:
        """Root endpoint returning service identity and documentation paths."""
        return {
            "name": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "status": "online",
            "environment": settings.ENVIRONMENT,
            "docs": "/docs",
            "api_v1": settings.API_V1_STR,
        }

    # Root-level health check alias for cloud load balancers & container monitors
    @application.get(
        "/healthz",
        status_code=status.HTTP_200_OK,
        summary="Root Healthcheck Alias",
        tags=["Health"],
    )
    async def root_healthz() -> dict[str, str]:
        """Root healthcheck probe alias for cloud platform monitoring."""
        return {
            "status": "ok",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
        }

    # Mount API v1 router
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "src.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
