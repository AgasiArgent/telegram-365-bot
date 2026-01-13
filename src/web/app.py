"""Flask application factory for Telegram 365 Bot web panel."""
from flask import Flask

from src.config import config


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="templates")

    # Configure app
    app.secret_key = config.SECRET_KEY

    # Register routes
    from src.web.routes import bp

    app.register_blueprint(bp)

    return app
