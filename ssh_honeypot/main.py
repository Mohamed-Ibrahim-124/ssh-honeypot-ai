"""
Main FastAPI application
Clean architecture implementation for SSH Honeypot
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from .config import settings
from .routers import analytics, health, honeypot
from .services.honeypot_service import HoneypotService
from .services.service_manager import set_honeypot_service
from .utils.logging import get_logger, setup_logging


# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management"""
    # Startup
    logger.info("Starting SSH Honeypot application...")
    logger.info(f"Configuration: {settings.app_name} v{settings.app_version}")

    # Initialize honeypot service
    honeypot_service = HoneypotService()
    await honeypot_service.initialize()

    # Set the initialized service in the service manager
    set_honeypot_service(honeypot_service)

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down SSH Honeypot application...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered SSH honeypot with clean FastAPI architecture",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
if settings.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors"""
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "detail": str(exc),
            "timestamp": "2024-01-01T00:00:00Z",  # Would use datetime.now().isoformat()
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred",
            "timestamp": "2024-01-01T00:00:00Z",  # Would use datetime.now().isoformat()
        },
    )


# Include routers
app.include_router(honeypot.router)
app.include_router(analytics.router)
app.include_router(health.router)


@app.get("/")
async def root() -> RedirectResponse:
    """Root endpoint - redirect to honeypot interface"""
    return RedirectResponse(url="/api/v1/")


# Dependency to get honeypot service is now handled by service_manager


if __name__ == "__main__":
    import uvicorn

    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "ssh_honeypot.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
