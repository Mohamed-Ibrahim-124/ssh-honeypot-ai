"""
Logging configuration and utilities
"""

import logging
import sys
from typing import Optional

from ..config import settings


def setup_logging() -> None:
    """Setup application logging"""
    import os

    # For Windows, try to enable UTF-8 console output
    if os.name == "nt":  # Windows
        try:
            # Enable UTF-8 mode for Windows console

            if hasattr(sys.stdout, "reconfigure"):
                sys.stdout.reconfigure(encoding="utf-8")
                sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass  # Fall back to default if UTF-8 mode fails

    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler("honeypot.log", encoding="utf-8")

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format,
        handlers=[console_handler, file_handler],
    )


def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)


class HoneypotLogger:
    """Custom logger for honeypot operations"""

    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(name)

    def log_command(self, session_id: str, command: str, threat_level: str) -> None:
        """Log command execution"""
        self.logger.info(
            f"Command executed - Session: {session_id}, Command: {command}, Threat: {threat_level}"
        )

    def log_session(
        self, session_id: str, action: str, details: Optional[str] = None
    ) -> None:
        """Log session events"""
        message = f"Session {action} - ID: {session_id}"
        if details:
            message += f", Details: {details}"
        self.logger.info(message)

    def log_threat(self, session_id: str, threat_level: str, command: str) -> None:
        """Log threat detection"""
        self.logger.warning(
            f"Threat detected - Session: {session_id}, Level: {threat_level}, Command: {command}"
        )

    def log_error(self, error: str, context: Optional[str] = None) -> None:
        """Log errors"""
        message = f"Error: {error}"
        if context:
            message += f", Context: {context}"
        self.logger.error(message)
