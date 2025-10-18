"""
Health check endpoints
Provides health monitoring and service status
"""

from datetime import datetime

from fastapi import APIRouter

from ..models.schemas import HealthStatus
from ..utils.logging import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthStatus)
async def health_check() -> HealthStatus:
    """Basic health check endpoint"""
    return HealthStatus(
        status="healthy",
        version="1.0.0",
        services={
            "api": "available",
            "database": "available",
            "ai_service": "available",
        },
    )


@router.get("/ping")
async def ping() -> dict[str, str]:
    """Simple ping endpoint"""
    return {"message": "pong", "timestamp": datetime.now().isoformat()}
