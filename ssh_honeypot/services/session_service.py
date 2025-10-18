"""
Session Management Service
Handles honeypot sessions and threat analysis
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

from ..core.honeypot import HoneypotCore
from ..models.schemas import SessionInfo


logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing honeypot sessions"""

    def __init__(self) -> None:
        self.active_sessions: Dict[str, Dict] = {}
        self.honeypot_core = HoneypotCore()
        self.max_sessions = 1000  # Prevent memory issues

    async def create_session(self, ip_address: str = "127.0.0.1") -> str:
        """Create new honeypot session"""
        # Clean up old sessions if needed
        if len(self.active_sessions) >= self.max_sessions:
            await self._cleanup_old_sessions()

        session_id = f"session_{int(time.time())}_{len(self.active_sessions)}"

        self.active_sessions[session_id] = {
            "start_time": datetime.now().isoformat(),
            "commands_executed": 0,
            "last_command": None,
            "ip_address": ip_address,
            "user_agent": "SSH-Client",
            "threat_level": "low",
            "last_activity": datetime.now().isoformat(),
        }

        logger.info(f"New session created: {session_id} from {ip_address}")
        return session_id

    async def process_command(self, session_id: str, command: str) -> tuple[str, str]:
        """Update session with command information (LLM-only approach)"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")

        # Get threat level from honeypot core (still needed for security analysis)
        _, threat_level = self.honeypot_core.process_command(command)

        # Update session
        session = self.active_sessions[session_id]
        session["commands_executed"] += 1
        session["last_command"] = command
        session["last_activity"] = datetime.now().isoformat()

        # Update threat level if higher
        if threat_level == "high" or (
            threat_level == "medium" and session["threat_level"] == "low"
        ):
            session["threat_level"] = threat_level

        logger.info(
            f"Session updated for {session_id}: {command} (threat: {threat_level})"
        )
        return "", threat_level  # Return empty response since LLM handles it

    async def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information"""
        if session_id not in self.active_sessions:
            return None

        session = self.active_sessions[session_id]
        return SessionInfo(
            session_id=session_id,
            start_time=session["start_time"],
            commands_executed=session["commands_executed"],
            last_command=session["last_command"],
            threat_level=session["threat_level"],
            ip_address=session["ip_address"],
        )

    async def get_all_sessions(self) -> List[SessionInfo]:
        """Get all active sessions"""
        sessions = []
        for session_id, session_data in self.active_sessions.items():
            sessions.append(
                SessionInfo(
                    session_id=session_id,
                    start_time=session_data["start_time"],
                    commands_executed=session_data["commands_executed"],
                    last_command=session_data["last_command"],
                    threat_level=session_data["threat_level"],
                    ip_address=session_data["ip_address"],
                )
            )
        return sessions

    async def close_session(self, session_id: str) -> bool:
        """Close a session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"Session closed: {session_id}")
            return True
        return False

    async def _cleanup_old_sessions(self) -> None:
        """Clean up old sessions"""
        current_time = datetime.now()
        sessions_to_remove = []

        for session_id, session_data in self.active_sessions.items():
            last_activity = datetime.fromisoformat(session_data["last_activity"])
            if (current_time - last_activity).seconds > 3600:  # 1 hour timeout
                sessions_to_remove.append(session_id)

        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]

        logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")

    def get_session_stats(self) -> Dict:
        """Get session statistics"""
        total_sessions = len(self.active_sessions)
        threat_levels: Dict[str, int] = {}

        for session in self.active_sessions.values():
            threat_level = session["threat_level"]
            threat_levels[threat_level] = threat_levels.get(threat_level, 0) + 1

        return {
            "total_sessions": total_sessions,
            "threat_distribution": threat_levels,
            "max_sessions": self.max_sessions,
        }
