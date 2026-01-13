"""Telegram bot package for Telegram 365 Bot."""
from src.bot.handlers import setup_handlers
from src.bot.bot import bot, dp

__all__ = ["bot", "dp", "setup_handlers"]
