"""Flask application factory for Telegram 365 Bot web panel."""
import logging
from datetime import timedelta

from flask import Flask, render_template

from src.config import config

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="templates")

    # Configure app
    app.secret_key = config.SECRET_KEY

    # Configure session timeout
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
        minutes=config.SESSION_TIMEOUT_MINUTES
    )

    # Register routes
    from src.web.routes import bp

    app.register_blueprint(bp)

    # Register error handlers
    @app.errorhandler(500)
    def internal_server_error(e):
        """Handle internal server errors with user-friendly message."""
        logger.error(f"Internal server error: {e}")
        return render_template(
            "error.html",
            error_title="Server Error",
            error_message="Something went wrong on our end. Please try again later.",
        ), 500

    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors."""
        return render_template(
            "error.html",
            error_title="Page Not Found",
            error_message="The page you're looking for doesn't exist.",
        ), 404

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle all unhandled exceptions."""
        # Log the error but don't expose details to user
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return render_template(
            "error.html",
            error_title="Error",
            error_message="An unexpected error occurred. Please try again later.",
        ), 500

    return app
