"""
Helper functions and utilities
"""

import ipaddress
import re
from datetime import datetime
from typing import Dict, Optional


def validate_ip_address(ip: str) -> bool:
    """Validate IP address format"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def sanitize_command(command: str) -> str:
    """Sanitize command input"""
    # Remove potentially dangerous characters
    sanitized = re.sub(r"[;&|`$]", "", command)
    # Limit length
    return sanitized[:1000]


def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """Format timestamp for display"""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.isoformat()


def extract_command_parts(command: str) -> Dict[str, str]:
    """Extract command parts for analysis"""
    parts = command.strip().split()
    return {
        "command": parts[0] if parts else "",
        "args": " ".join(parts[1:]) if len(parts) > 1 else "",
        "full_command": command.strip(),
    }


def is_suspicious_command(command: str) -> bool:
    """Check if command is suspicious"""
    suspicious_patterns = [
        r"rm\s+-rf",
        r"sudo\s+",
        r"passwd\s+",
        r"su\s+",
        r"wget\s+",
        r"curl\s+",
        r"nc\s+",
        r"netcat\s+",
        r"python\s+-c",
        r"bash\s+-c",
        r"sh\s+-c",
    ]

    command_lower = command.lower()
    return any(re.search(pattern, command_lower) for pattern in suspicious_patterns)


def generate_session_id() -> str:
    """Generate unique session ID"""
    timestamp = int(datetime.now().timestamp())
    return f"session_{timestamp}"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size_float = float(size_bytes)
    while size_float >= 1024 and i < len(size_names) - 1:
        size_float /= 1024.0
        i += 1

    return f"{size_float:.1f}{size_names[i]}"
