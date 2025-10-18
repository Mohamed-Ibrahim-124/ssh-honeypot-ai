#!/usr/bin/env python3
"""
Custom Configuration Example
"""

import uvicorn

from ssh_honeypot.config import settings
from ssh_honeypot.main import app


def setup_custom_config():
    """Setup custom configuration for the honeypot"""

    # AI Model Configuration
    settings.ai_model_name = "microsoft/DialoGPT-medium"  # Use medium model
    settings.ai_model_device = "cuda"  # Force GPU usage
    settings.ai_max_tokens = 150  # Increase token limit

    # Server Configuration
    settings.host = "0.0.0.0"  # Listen on all interfaces
    settings.port = 8080
    settings.debug = True  # Enable debug mode

    # Security Configuration
    settings.enable_cors = True
    settings.log_level = "DEBUG"

    print("Custom configuration applied:")
    print(f"Model: {settings.ai_model_name}")
    print(f"Device: {settings.ai_model_device}")
    print(f"Host: {settings.host}:{settings.port}")
    print(f"Debug: {settings.debug}")


def run_honeypot():
    """Run the honeypot with custom configuration"""
    setup_custom_config()

    print("Starting SSH Honeypot with custom configuration...")
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run_honeypot()
