"""Configuration management for Telegram 365 Bot."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/telegram_365_bot")

    # Admin Authentication
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "")

    # Web Panel
    WEB_ADMIN_PASSWORD: str = os.getenv("WEB_ADMIN_PASSWORD", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key")

    # Flask Server
    FLASK_HOST: str = os.getenv("FLASK_HOST", "0.0.0.0")
    FLASK_PORT: int = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"

    # Session timeout in minutes (default: 30 minutes)
    SESSION_TIMEOUT_MINUTES: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))

    # Scheduler
    SCHEDULER_TIMEZONE: str = os.getenv("SCHEDULER_TIMEZONE", "UTC")

    # Message limits
    MAX_MESSAGE_LENGTH: int = 4096  # Telegram message limit
    TOTAL_DAYS: int = 365

    @classmethod
    def validate(cls) -> list[str]:
        """Validate required configuration.

        Returns:
            List of missing configuration keys.
        """
        errors = []
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is required")
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL is required")
        if not cls.ADMIN_PASSWORD:
            errors.append("ADMIN_PASSWORD is required")
        if not cls.WEB_ADMIN_PASSWORD:
            errors.append("WEB_ADMIN_PASSWORD is required")
        return errors


config = Config()
