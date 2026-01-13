"""Database session management for Telegram 365 Bot."""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.config import config
from src.database.models import Base, Message, Setting

# Create database engine
engine = create_engine(config.DATABASE_URL, pool_pre_ping=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize the database and create all tables."""
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Initialize 365 messages if they don't exist
    with get_db() as db:
        existing_count = db.query(Message).count()
        if existing_count < config.TOTAL_DAYS:
            for day in range(1, config.TOTAL_DAYS + 1):
                existing = db.query(Message).filter(Message.day_number == day).first()
                if not existing:
                    message = Message(day_number=day, content="")
                    db.add(message)
            db.commit()

        # Initialize welcome message setting if not exists
        welcome_setting = (
            db.query(Setting).filter(Setting.key == "welcome_message").first()
        )
        if not welcome_setting:
            welcome = Setting(
                key="welcome_message",
                value="Welcome! You'll receive a daily message for the next 365 days.",
            )
            db.add(welcome)
            db.commit()


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session context manager.

    Yields:
        SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
