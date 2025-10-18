"""
Service Manager
Centralized service instance management for the SSH Honeypot
"""

from typing import Optional

from .honeypot_service import HoneypotService

# Global service instance
_honeypot_service_instance: Optional[HoneypotService] = None


def get_honeypot_service() -> HoneypotService:
    """Get the singleton honeypot service instance"""
    global _honeypot_service_instance
    if _honeypot_service_instance is None:
        _honeypot_service_instance = HoneypotService()
    return _honeypot_service_instance


def set_honeypot_service(service: HoneypotService) -> None:
    """Set the global honeypot service instance (used by main.py)"""
    global _honeypot_service_instance
    _honeypot_service_instance = service


def initialize_services() -> HoneypotService:
    """Initialize all services and return the service instance"""
    service = get_honeypot_service()
    # Services are initialized lazily when first used
    return service


def reset_services() -> None:
    """Reset services (useful for testing)"""
    global _honeypot_service_instance
    _honeypot_service_instance = None
