#!/usr/bin/env python3
"""
Basic SSH Honeypot Usage Example
"""

import asyncio

from ssh_honeypot.services.ai_service import AIModelService


async def test_honeypot():
    """Test the honeypot with various commands"""

    # Initialize AI service
    ai_service = AIModelService()
    await ai_service.initialize_model()

    # Test commands
    test_commands = ["ls", "pwd", "who", "cat /etc/passwd", "unknown_command"]

    print("Testing SSH Honeypot AI Service")
    print("=" * 40)

    for command in test_commands:
        try:
            response = await ai_service.generate_response(command)
            print(f"Command: {command}")
            print(f"Response: {response}")
            print("-" * 30)
        except Exception as e:
            print(f"Error with {command}: {e}")
            print("-" * 30)


if __name__ == "__main__":
    asyncio.run(test_honeypot())
