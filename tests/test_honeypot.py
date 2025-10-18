"""
Tests for SSH Honeypot
Basic test coverage for core functionality
"""

import pytest
from fastapi.testclient import TestClient

from ssh_honeypot.core.honeypot import FakeSystem, HoneypotCore
from ssh_honeypot.main import app
from ssh_honeypot.models.schemas import CommandRequest
from ssh_honeypot.services.session_service import SessionService


client = TestClient(app)


class TestFakeSystem:
    """Test fake system functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.fake_system = FakeSystem()

    def test_ls_command(self):
        """Test ls command"""
        result = self.fake_system.execute_ls("/")
        assert "bin" in result
        assert "etc" in result
        assert "home" in result

    def test_ls_nonexistent_path(self):
        """Test ls with nonexistent path"""
        result = self.fake_system.execute_ls("/nonexistent")
        assert "No such file or directory" in result

    def test_cat_passwd(self):
        """Test cat /etc/passwd command"""
        result = self.fake_system.execute_cat_passwd()
        assert "root:x:0:0:root:/root:/bin/bash" in result
        assert "admin:x:1000:1000:admin" in result

    def test_who_command(self):
        """Test who command"""
        result = self.fake_system.execute_who()
        assert "admin" in result
        assert "student" in result
        assert "root" in result

    def test_pwd_command(self):
        """Test pwd command"""
        result = self.fake_system.execute_pwd()
        assert result == "/home/admin"

    def test_cd_command(self):
        """Test cd command"""
        result = self.fake_system.execute_cd("/home")
        assert "Changed directory to /home" in result

        result = self.fake_system.execute_cd("/nonexistent")
        assert "No such file or directory" in result


class TestHoneypotCore:
    """Test honeypot core functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.honeypot = HoneypotCore()

    def test_process_command_ls(self):
        """Test processing ls command"""
        response, threat_level = self.honeypot.process_command("ls")
        assert "bin" in response
        assert threat_level == "low"

    def test_process_command_suspicious(self):
        """Test processing suspicious command"""
        response, threat_level = self.honeypot.process_command("sudo rm -rf /")
        assert threat_level == "high"

    def test_process_command_help(self):
        """Test processing help command"""
        response, threat_level = self.honeypot.process_command("help")
        assert "Available commands" in response
        assert threat_level == "low"

    def test_process_command_exit(self):
        """Test processing exit command"""
        response, threat_level = self.honeypot.process_command("exit")
        assert response == "Goodbye!"
        assert threat_level == "low"


class TestSessionService:
    """Test session service functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.session_service = SessionService()

    @pytest.mark.asyncio
    async def test_create_session(self):
        """Test session creation"""
        session_id = await self.session_service.create_session("192.168.1.1")
        assert session_id.startswith("session_")
        assert session_id in self.session_service.active_sessions

    @pytest.mark.asyncio
    async def test_process_command(self):
        """Test command processing"""
        session_id = await self.session_service.create_session()
        response, threat_level = await self.session_service.process_command(
            session_id, "ls"
        )
        assert "bin" in response
        assert threat_level == "low"

        # Check session was updated
        session = self.session_service.active_sessions[session_id]
        assert session["commands_executed"] == 1
        assert session["last_command"] == "ls"

    @pytest.mark.asyncio
    async def test_get_session_info(self):
        """Test getting session info"""
        session_id = await self.session_service.create_session()
        session_info = await self.session_service.get_session_info(session_id)
        assert session_info.session_id == session_id
        assert session_info.commands_executed == 0


class TestAPI:
    """Test API endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 307  # Redirect

    def test_honeypot_interface(self):
        """Test honeypot web interface"""
        response = client.get("/api/v1/")
        assert response.status_code == 200
        assert "SSH Honeypot" in response.text

    def test_command_endpoint(self):
        """Test command processing endpoint"""
        response = client.post("/api/v1/command", json={"command": "ls"})
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "command" in data
        assert "timestamp" in data
        assert "session_id" in data

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_ping_endpoint(self):
        """Test ping endpoint"""
        response = client.get("/api/v1/ping")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "pong"

    def test_analytics_endpoint(self):
        """Test analytics endpoint"""
        response = client.get("/api/v1/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "total_attacks" in data
        assert "unique_sessions" in data

    def test_sessions_endpoint(self):
        """Test sessions endpoint"""
        response = client.get("/api/v1/sessions")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestModels:
    """Test Pydantic models"""

    def test_command_request(self):
        """Test CommandRequest model"""
        request = CommandRequest(command="ls")
        assert request.command == "ls"
        assert request.session_id is None

    def test_command_request_with_session(self):
        """Test CommandRequest with session"""
        request = CommandRequest(command="ls", session_id="test_session")
        assert request.command == "ls"
        assert request.session_id == "test_session"

    def test_command_request_validation(self):
        """Test CommandRequest validation"""
        with pytest.raises(ValueError):
            CommandRequest(command="")  # Empty command should fail


if __name__ == "__main__":
    pytest.main([__file__])
