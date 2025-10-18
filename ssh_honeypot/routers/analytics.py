"""
Analytics API endpoints
Provides analytics and monitoring data
"""

from fastapi import APIRouter, Depends, HTTPException

from ..models.schemas import AnalyticsData, HealthStatus
from ..services.honeypot_service import HoneypotService
from ..services.service_manager import get_honeypot_service
from ..utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["analytics"])


@router.get("/analytics", response_model=AnalyticsData)
async def get_analytics(
    honeypot_service: HoneypotService = Depends(get_honeypot_service),
) -> AnalyticsData:
    """Get honeypot analytics data"""
    try:
        analytics = await honeypot_service.get_analytics()
        return analytics
    except Exception as e:
        logger.error(f"Failed to get analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from None


@router.get("/status", response_model=HealthStatus)
async def get_status(
    honeypot_service: HoneypotService = Depends(get_honeypot_service),
) -> HealthStatus:
    """Get service status and health information"""
    try:
        service_status = honeypot_service.get_service_status()

        # Determine overall health
        overall_status = "healthy"
        if not service_status["ai_service"]["available"]:
            overall_status = "degraded"

        return HealthStatus(
            status=overall_status,
            version="1.0.0",
            services={
                "ai_service": "available"
                if service_status["ai_service"]["available"]
                else "unavailable",
                "session_service": "available",
                "analytics_service": "available",
            },
        )
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from None
