"""Database query functions for Telegram 365 Bot."""
from datetime import date, time as dt_time
from typing import Optional

from sqlalchemy.orm import Session

from src.database.models import User, Message, Setting, Admin
from src.config import config


# User queries
def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
    """Get user by Telegram ID."""
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def create_user(
    db: Session,
    telegram_id: int,
    username: Optional[str] = None,
    timezone: str = "UTC",
) -> User:
    """Create a new user."""
    user = User(
        telegram_id=telegram_id,
        username=username,
        timezone=timezone,
        current_day=1,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user_day(db: Session, user: User, user_date: date = None) -> User:
    """Increment user's current day, cycling back to 1 after 365."""
    user.last_message_date = user_date or date.today()
    if user.current_day >= config.TOTAL_DAYS:
        user.current_day = 1
    else:
        user.current_day += 1
    db.commit()
    db.refresh(user)
    return user


def set_user_active(db: Session, user: User, is_active: bool) -> User:
    """Set user active status."""
    user.is_active = is_active
    db.commit()
    db.refresh(user)
    return user


def get_users_for_delivery(db: Session) -> list[User]:
    """Get all active users for message delivery check."""
    return db.query(User).filter(User.is_active == True).all()


# Message queries
def get_message_by_day(db: Session, day_number: int) -> Optional[Message]:
    """Get message for a specific day."""
    return db.query(Message).filter(Message.day_number == day_number).first()


def get_all_messages(db: Session) -> list[Message]:
    """Get all messages ordered by day number."""
    return db.query(Message).order_by(Message.day_number).all()


def update_message(
    db: Session,
    day_number: int,
    content: str,
    send_time: Optional[dt_time] = None,
) -> Optional[Message]:
    """Update message content and optionally send time."""
    message = get_message_by_day(db, day_number)
    if message:
        message.content = content
        if send_time:
            message.send_time = send_time
        db.commit()
        db.refresh(message)
    return message


# Settings queries
def get_setting(db: Session, key: str) -> Optional[str]:
    """Get setting value by key."""
    setting = db.query(Setting).filter(Setting.key == key).first()
    return setting.value if setting else None


def set_setting(db: Session, key: str, value: str) -> Setting:
    """Set or update a setting value."""
    setting = db.query(Setting).filter(Setting.key == key).first()
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value)
        db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


def get_welcome_message(db: Session) -> str:
    """Get the welcome message."""
    return get_setting(db, "welcome_message") or "Welcome!"


def set_welcome_message(db: Session, message: str) -> Setting:
    """Set the welcome message."""
    return set_setting(db, "welcome_message", message)


# Admin queries
def is_admin(db: Session, telegram_id: int) -> bool:
    """Check if user is an admin."""
    admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
    return admin is not None


def add_admin(db: Session, telegram_id: int) -> Admin:
    """Add a new admin."""
    admin = Admin(telegram_id=telegram_id)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def remove_admin(db: Session, telegram_id: int) -> bool:
    """Remove an admin."""
    admin = db.query(Admin).filter(Admin.telegram_id == telegram_id).first()
    if admin:
        db.delete(admin)
        db.commit()
        return True
    return False
