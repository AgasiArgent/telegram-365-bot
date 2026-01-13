"""Main entry point for Telegram 365 Bot."""
import asyncio
import logging
import sys
import threading

from src.config import config
from src.database import init_db
from src.bot import bot, dp, setup_handlers
from src.scheduler import setup_scheduler
from src.web import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


def run_flask():
    """Run Flask web server in a separate thread."""
    app = create_app()
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=False,  # Don't use debug mode in thread
        use_reloader=False,  # Don't use reloader in thread
    )


async def main():
    """Main application entry point."""
    # Validate configuration
    errors = config.validate()
    if errors:
        for error in errors:
            logger.error(error)
        logger.error("Please configure the required environment variables in .env file")
        sys.exit(1)

    # Initialize database
    logger.info("Initializing database...")
    init_db()

    # Setup bot handlers
    logger.info("Setting up bot handlers...")
    setup_handlers(dp)

    # Setup scheduler
    logger.info("Starting scheduler...")
    setup_scheduler()

    # Start Flask in a separate thread
    logger.info(f"Starting web panel on http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Start bot polling
    logger.info("Starting Telegram bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
