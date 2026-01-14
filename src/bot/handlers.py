"""Telegram bot command handlers for Telegram 365 Bot."""
import logging
from datetime import time as dt_time

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from src.config import config
from src.database import get_db
from src.database import queries

logger = logging.getLogger(__name__)

# Create router
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle /start command - welcome new users or returning users."""
    telegram_id = message.from_user.id
    username = message.from_user.username

    with get_db() as db:
        # Check if user exists
        user = queries.get_user_by_telegram_id(db, telegram_id)

        if user:
            # Returning user - reactivate if inactive
            if not user.is_active:
                queries.set_user_active(db, user, True)
                logger.info(f"User {telegram_id} reactivated at day {user.current_day}")
        else:
            # New user - create account
            user = queries.create_user(
                db,
                telegram_id=telegram_id,
                username=username,
                timezone="UTC",  # TODO: Implement timezone detection
            )
            logger.info(f"New user {telegram_id} registered")

        # Send welcome message
        welcome = queries.get_welcome_message(db)
        await message.answer(welcome)


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    """Handle /admin <password> command - grant admin access."""
    telegram_id = message.from_user.id

    # Extract password from command
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        # Don't reveal that this is an admin command
        return

    password = args[1].strip()

    if password == config.ADMIN_PASSWORD:
        with get_db() as db:
            if not queries.is_admin(db, telegram_id):
                queries.add_admin(db, telegram_id)
                logger.info(f"Admin access granted to {telegram_id}")

            await message.answer("Admin access granted.")
    else:
        # Log failed attempt but don't reveal it's wrong
        logger.warning(f"Failed admin login attempt from {telegram_id}")


@router.message(Command("welcome"))
async def cmd_welcome(message: Message) -> None:
    """Handle /welcome command - view current welcome message (admin only)."""
    telegram_id = message.from_user.id

    with get_db() as db:
        if not queries.is_admin(db, telegram_id):
            return

        welcome = queries.get_welcome_message(db)
        await message.answer(f"Current welcome message:\n\n{welcome}")


@router.message(Command("setwelcome"))
async def cmd_setwelcome(message: Message) -> None:
    """Handle /setwelcome <text> command - update welcome message (admin only)."""
    telegram_id = message.from_user.id

    with get_db() as db:
        if not queries.is_admin(db, telegram_id):
            return

        # Extract new welcome message
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("Usage: /setwelcome <message text>")
            return

        new_welcome = args[1].strip()

        if len(new_welcome) > config.MAX_MESSAGE_LENGTH:
            await message.answer(
                f"Message too long. Maximum {config.MAX_MESSAGE_LENGTH} characters."
            )
            return

        queries.set_welcome_message(db, new_welcome)
        logger.info(f"Welcome message updated by admin {telegram_id}")
        await message.answer("Welcome message updated successfully.")


@router.message(Command("day"))
async def cmd_day(message: Message) -> None:
    """Handle /day <number> command - view message for specific day (admin only)."""
    telegram_id = message.from_user.id

    with get_db() as db:
        if not queries.is_admin(db, telegram_id):
            return

        # Extract day number
        args = message.text.split()
        if len(args) < 2:
            await message.answer("Usage: /day <number> (1-365)")
            return

        try:
            day_number = int(args[1])
        except ValueError:
            await message.answer("Please provide a valid day number (1-365).")
            return

        if day_number < 1 or day_number > config.TOTAL_DAYS:
            await message.answer(f"Day number must be between 1 and {config.TOTAL_DAYS}.")
            return

        msg = queries.get_message_by_day(db, day_number)
        if msg:
            content = msg.content or "(empty)"
            send_time = msg.send_time.strftime("%H:%M") if msg.send_time else "09:00"
            await message.answer(
                f"Day {day_number} (sends at {send_time}):\n\n{content}"
            )
        else:
            await message.answer(f"No message found for day {day_number}.")


@router.message(Command("setday"))
async def cmd_setday(message: Message) -> None:
    """Handle /setday <number> <text> command - update day message (admin only)."""
    telegram_id = message.from_user.id

    with get_db() as db:
        if not queries.is_admin(db, telegram_id):
            return

        # Extract day number and message
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.answer("Usage: /setday <number> <message text>")
            return

        try:
            day_number = int(args[1])
        except ValueError:
            await message.answer("Please provide a valid day number (1-365).")
            return

        if day_number < 1 or day_number > config.TOTAL_DAYS:
            await message.answer(f"Day number must be between 1 and {config.TOTAL_DAYS}.")
            return

        new_content = args[2].strip()

        if len(new_content) > config.MAX_MESSAGE_LENGTH:
            await message.answer(
                f"Message too long. Maximum {config.MAX_MESSAGE_LENGTH} characters."
            )
            return

        queries.update_message(db, day_number, new_content)
        logger.info(f"Day {day_number} message updated by admin {telegram_id}")
        await message.answer(f"Day {day_number} message updated successfully.")


@router.message(Command("settime"))
async def cmd_settime(message: Message) -> None:
    """Handle /settime <day> <HH:MM> command - set send time for a day (admin only)."""
    telegram_id = message.from_user.id

    with get_db() as db:
        if not queries.is_admin(db, telegram_id):
            return

        # Extract day number and time
        args = message.text.split()
        if len(args) < 3:
            await message.answer("Usage: /settime <day> <HH:MM>\nExample: /settime 1 14:30")
            return

        try:
            day_number = int(args[1])
        except ValueError:
            await message.answer("Please provide a valid day number (1-365).")
            return

        if day_number < 1 or day_number > config.TOTAL_DAYS:
            await message.answer(f"Day number must be between 1 and {config.TOTAL_DAYS}.")
            return

        # Parse time
        time_str = args[2].strip()
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                raise ValueError("Invalid format")
            hour = int(parts[0])
            minute = int(parts[1])
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("Invalid time values")
            send_time = dt_time(hour, minute)
        except (ValueError, IndexError):
            await message.answer("Invalid time format. Use HH:MM (e.g., 14:30)")
            return

        # Get current message content to preserve it
        msg = queries.get_message_by_day(db, day_number)
        if msg:
            queries.update_message(db, day_number, msg.content, send_time)
            logger.info(f"Day {day_number} time set to {time_str} by admin {telegram_id}")
            await message.answer(f"Day {day_number} send time set to {time_str}.")
        else:
            await message.answer(f"No message found for day {day_number}.")


def setup_handlers(dp) -> None:
    """Register all handlers with the dispatcher."""
    dp.include_router(router)
