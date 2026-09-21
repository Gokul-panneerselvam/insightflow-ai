"""Health check endpoints for deployment probes and monitoring."""

from datetime import UTC, datetime

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from src.app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """General health response schema."""

    status: str = Field(default="healthy", description="Application health status")
    app_name: str = Field(..., description="Name of the application")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Runtime environment")
    timestamp: datetime = Field(
        ..., description="UTC ISO timestamp of the health check"
    )


class LivenessResponse(BaseModel):
    """Liveness probe response schema."""

    status: str = Field(default="alive", description="Liveness status")
    timestamp: datetime = Field(
        ..., description="UTC ISO timestamp of the liveness probe"
    )


class ReadinessResponse(BaseModel):
    """Readiness probe response schema."""

    status: str = Field(default="ready", description="Readiness status")
    checks: dict[str, str] = Field(
        ..., description="Individual subsystem readiness checks"
    )
    timestamp: datetime = Field(
        ..., description="UTC ISO timestamp of the readiness probe"
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Application Health Check",
    description="Returns detailed application status, version, and timestamp.",
)
async def health_check() -> HealthResponse:
    """Get application health status."""
    return HealthResponse(
        status="healthy",
        app_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(UTC),
    )


@router.get(
    "/livez",
    response_model=LivenessResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness Probe",
    description="Container liveness probe to verify server process is alive.",
)
async def liveness_probe() -> LivenessResponse:
    """Get server liveness probe status."""
    return LivenessResponse(
        status="alive",
        timestamp=datetime.now(UTC),
    )


@router.get(
    "/readyz",
    response_model=ReadinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness Probe",
    description="Readiness probe to verify application is prepared for traffic.",
)
async def readiness_probe() -> ReadinessResponse:
    """Get server readiness probe status."""
    # Add dependency/database checks here as the application expands
    checks = {
        "server": "ok",
        "api": "ready",
    }
    return ReadinessResponse(
        status="ready",
        checks=checks,
        timestamp=datetime.now(UTC),
    )
