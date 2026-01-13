"""SQLAlchemy models for Telegram 365 Bot."""
from datetime import datetime, time
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Text,
    Boolean,
    DateTime,
    Time,
    Date,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    """User model for tracking Telegram users."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    timezone = Column(String(50), default="UTC")
    current_day = Column(Integer, default=1)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_message_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<User(telegram_id={self.telegram_id}, day={self.current_day})>"


class Message(Base):
    """Message model for daily messages."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    day_number = Column(Integer, unique=True, nullable=False, index=True)
    content = Column(Text, default="")
    send_time = Column(Time, default=time(9, 0))  # Default 09:00
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Message(day={self.day_number})>"


class Setting(Base):
    """Settings model for key-value configuration."""

    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Setting(key={self.key})>"


class Admin(Base):
    """Admin model for tracking authorized admins."""

    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    granted_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Admin(telegram_id={self.telegram_id})>"
