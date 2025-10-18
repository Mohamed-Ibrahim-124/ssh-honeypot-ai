"""
Configuration management for SSH Honeypot
Handles environment variables and application settings
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Application settings
    app_name: str = "SSH Honeypot"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # AI Model settings - Multiple options for different use cases
    ai_model_name: str = (
        "microsoft/DialoGPT-small"  # Primary: Good for conversational responses
    )
    ai_model_fallback: str = "distilgpt2"  # Fallback: Lightweight and fast
    ai_model_device: str = "auto"  # auto, cpu, cuda
    ai_max_tokens: int = 150
    ai_temperature: float = 0.6
    ai_use_quantized: bool = True  # Enable quantized models for better performance

    # Honeypot settings
    fake_system_enabled: bool = True
    session_timeout: int = 3600  # 1 hour
    max_commands_per_session: int = 100

    # Security settings
    enable_cors: bool = True
    cors_origins: list = ["*"]

    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
