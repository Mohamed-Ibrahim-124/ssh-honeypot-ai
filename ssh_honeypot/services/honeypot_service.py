"""
Honeypot Service
Main business logic for honeypot operations
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from ..models.schemas import AnalyticsData, CommandResponse, SessionInfo
from .ai_service import AIModelService
from .session_service import SessionService

logger = logging.getLogger(__name__)


class HoneypotService:
    """Main honeypot service coordinating all operations"""

    def __init__(self) -> None:
        self.ai_service = AIModelService()
        self.session_service = SessionService()
        self.attack_logs: List[Dict] = []

    async def initialize(self) -> bool:
        """Initialize all services"""
        logger.info("Initializing honeypot services...")

        # Initialize AI service
        ai_initialized = await self.ai_service.initialize_model()
        if not ai_initialized:
            logger.warning("AI service initialization failed, continuing with fallback")

        logger.info("Honeypot services initialized successfully")
        return True

    async def process_command(
        self,
        command: str,
        session_id: Optional[str] = None,
        ip_address: str = "127.0.0.1",
    ) -> CommandResponse:
        """Process SSH command through honeypot"""
        try:
            # Create session if not provided
            if not session_id:
                session_id = await self.session_service.create_session(ip_address)

            # LLM-only approach: Use AI for all responses
            if not self.ai_service.is_available():
                logger.warning("AI service is not available, using fallback responses")

            # Generate response using LLM with fallback
            response = await self.ai_service.generate_response(command)

            # Get threat level from core (still needed for security analysis)
            _, threat_level = self.session_service.honeypot_core.process_command(
                command
            )

            logger.info(f"LLM generated response for command: {command}")

            # Log attack
            await self._log_attack(session_id, command, response, threat_level)

            return CommandResponse(
                response=response,
                command=command,
                timestamp=datetime.now().isoformat(),
                session_id=session_id,
                threat_level=threat_level,
            )

        except Exception as e:
            logger.error(f"Command processing failed: {e}")
            raise

    async def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information"""
        return await self.session_service.get_session_info(session_id)

    async def get_all_sessions(self) -> List[SessionInfo]:
        """Get all active sessions"""
        return await self.session_service.get_all_sessions()

    async def close_session(self, session_id: str) -> bool:
        """Close a session"""
        return await self.session_service.close_session(session_id)

    async def get_analytics(self) -> AnalyticsData:
        """Get analytics data"""
        # Get session statistics
        session_stats = self.session_service.get_session_stats()

        # Analyze attack logs
        common_commands = self._get_common_commands()
        threat_distribution = self._get_threat_distribution()

        return AnalyticsData(
            total_attacks=len(self.attack_logs),
            unique_sessions=session_stats["total_sessions"],
            common_commands=common_commands,
            threat_distribution=threat_distribution,
        )

    async def _log_attack(
        self, session_id: str, command: str, response: str, threat_level: str
    ) -> None:
        """Log attack for analysis"""
        attack_log = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "command": command,
            "response": response,
            "threat_level": threat_level,
        }

        self.attack_logs.append(attack_log)
        logger.info(
            f"Attack logged: {command} from {session_id} (threat: {threat_level})"
        )

    def _get_common_commands(self) -> Dict[str, int]:
        """Get most common attack commands"""
        commands = [log["command"] for log in self.attack_logs]
        command_counts: Dict[str, int] = {}

        for cmd in commands:
            command_counts[cmd] = command_counts.get(cmd, 0) + 1

        # Return top 10 most common commands
        return dict(
            sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        )

    def _get_threat_distribution(self) -> Dict[str, int]:
        """Get threat level distribution"""
        threats = [log["threat_level"] for log in self.attack_logs]
        threat_counts: Dict[str, int] = {}

        for threat in threats:
            threat_counts[threat] = threat_counts.get(threat, 0) + 1

        return threat_counts

    def get_service_status(self) -> Dict:
        """Get status of all services"""
        return {
            "ai_service": {
                "available": self.ai_service.is_available(),
                "model_info": self.ai_service.get_model_info(),
            },
            "session_service": {
                "active_sessions": len(self.session_service.active_sessions),
                "stats": self.session_service.get_session_stats(),
            },
            "attack_logs": {"total_logs": len(self.attack_logs)},
        }
