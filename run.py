#!/usr/bin/env python3
"""
SSH Honeypot Runner
Clean FastAPI architecture implementation
"""

import os
import sys

import uvicorn


# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ssh_honeypot.config import settings
from ssh_honeypot.main import app
from ssh_honeypot.utils.logging import get_logger, setup_logging


def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    logger = get_logger(__name__)

    # Use text alternatives for better Windows console compatibility
    logger.info("=" * 60)
    logger.info(f"[START] Starting {settings.app_name} v{settings.app_version}")
    logger.info("=" * 60)
    logger.info(f"[WEB] Web interface: http://{settings.host}:{settings.port}")
    logger.info(
        f"[DOCS] API documentation: http://{settings.host}:{settings.port}/docs"
    )
    logger.info(
        f"[HEALTH] Health check: http://{settings.host}:{settings.port}/api/v1/health"
    )
    logger.info("[ARCH] Architecture: Clean FastAPI with proper separation of concerns")
    logger.info(f"[AI] AI Model: {settings.ai_model_name}")
    logger.info("[SEC] Security: Fake commands only - safe for learning")
    logger.info("=" * 60)

    # Start the server
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main()
