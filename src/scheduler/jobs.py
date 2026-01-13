"""APScheduler jobs for Telegram 365 Bot."""
import asyncio
import logging
from datetime import datetime, date

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import config
from src.database import get_db
from src.database import queries
from src.bot.bot import bot

logger = logging.getLogger(__name__)

# Create scheduler
scheduler = AsyncIOScheduler(timezone=config.SCHEDULER_TIMEZONE)


async def send_daily_messages() -> None:
    """Check and send daily messages to users based on their timezone."""
    logger.debug("Running daily message check...")

    with get_db() as db:
        users = queries.get_users_for_delivery(db)

        for user in users:
            try:
                # Skip if already received message today
                if user.last_message_date == date.today():
                    continue

                # Get user's timezone
                try:
                    user_tz = pytz.timezone(user.timezone or "UTC")
                except pytz.exceptions.UnknownTimeZoneError:
                    user_tz = pytz.UTC

                # Get current time in user's timezone
                user_now = datetime.now(user_tz)

                # Get message for user's current day
                message = queries.get_message_by_day(db, user.current_day)
                if not message:
                    logger.warning(f"No message found for day {user.current_day}")
                    continue

                # Check if it's time to send (compare hours and minutes)
                send_time = message.send_time
                if (
                    user_now.hour == send_time.hour
                    and user_now.minute == send_time.minute
                ):
                    # Send message if content exists
                    if message.content:
                        try:
                            await bot.send_message(user.telegram_id, message.content)
                            logger.info(
                                f"Sent day {user.current_day} message to user {user.telegram_id}"
                            )

                            # Update user's day
                            queries.update_user_day(db, user)

                        except Exception as e:
                            logger.error(
                                f"Failed to send message to {user.telegram_id}: {e}"
                            )
                            # Mark user as inactive if blocked
                            if "blocked" in str(e).lower():
                                queries.set_user_active(db, user, False)
                                logger.info(
                                    f"User {user.telegram_id} marked inactive (blocked)"
                                )
                    else:
                        logger.warning(
                            f"Day {user.current_day} has empty content, skipping"
                        )

            except Exception as e:
                logger.error(f"Error processing user {user.telegram_id}: {e}")
                continue


def setup_scheduler() -> None:
    """Configure and start the scheduler."""
    # Run message check every minute
    scheduler.add_job(
        send_daily_messages,
        "interval",
        minutes=1,
        id="daily_message_check",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started - checking for messages every minute")
