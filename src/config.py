"""Configuration management for the copywriting engine."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
    logger.debug(f"Loaded environment variables from {ENV_PATH}")


class Config:
    """Centralized configuration with validation and defaults."""

    # Gemini API Settings
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Concurrency & Retry Settings
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "10"))
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "60"))
    RETRY_ATTEMPTS: int = int(os.getenv("RETRY_ATTEMPTS", "3"))
    BACKOFF_MULTIPLIER: float = float(os.getenv("BACKOFF_MULTIPLIER", "2.0"))
    JITTER_RANGE: float = float(os.getenv("JITTER_RANGE", "0.1"))

    # Default Generation Parameters
    DEFAULT_TEMPERATURE: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.7"))
    DEFAULT_TOP_P: float = float(os.getenv("DEFAULT_TOP_P", "0.9"))
    DEFAULT_MAX_TOKENS: int = int(os.getenv("DEFAULT_MAX_TOKENS", "500"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Paths
    PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
    PROMPTS_DIR: Path = PROJECT_ROOT / "prompts"
    OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"

    @classmethod
    def validate(cls) -> list[str]:
        """Validate critical configuration values."""

        errors: list[str] = []

        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is required but not set.")

        if cls.MAX_CONCURRENT_REQUESTS < 1:
            errors.append("MAX_CONCURRENT_REQUESTS must be at least 1.")

        if cls.RETRY_ATTEMPTS < 0:
            errors.append("RETRY_ATTEMPTS cannot be negative.")

        if not (0.0 <= cls.DEFAULT_TEMPERATURE <= 2.0):
            errors.append("DEFAULT_TEMPERATURE must be between 0.0 and 2.0.")

        if not (0.0 <= cls.DEFAULT_TOP_P <= 1.0):
            errors.append("DEFAULT_TOP_P must be between 0.0 and 1.0.")

        if cls.DEFAULT_MAX_TOKENS < 1:
            errors.append("DEFAULT_MAX_TOKENS must be at least 1.")

        return errors

    @classmethod
    def is_valid(cls) -> bool:
        """Check if configuration is valid."""
        return len(cls.validate()) == 0

    @classmethod
    def to_dict(cls) -> dict:
        """Return configuration as a dictionary (safe for logging)."""

        return {
            "GEMINI_MODEL": cls.GEMINI_MODEL,
            "MAX_CONCURRENT_REQUESTS": cls.MAX_CONCURRENT_REQUESTS,
            "REQUEST_TIMEOUT": cls.REQUEST_TIMEOUT,
            "RETRY_ATTEMPTS": cls.RETRY_ATTEMPTS,
            "BACKOFF_MULTIPLIER": cls.BACKOFF_MULTIPLIER,
            "JITTER_RANGE": cls.JITTER_RANGE,
            "DEFAULT_TEMPERATURE": cls.DEFAULT_TEMPERATURE,
            "DEFAULT_TOP_P": cls.DEFAULT_TOP_P,
            "DEFAULT_MAX_TOKENS": cls.DEFAULT_MAX_TOKENS,
            "LOG_LEVEL": cls.LOG_LEVEL,
        }
