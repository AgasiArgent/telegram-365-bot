"""Flask routes for Telegram 365 Bot web admin panel."""
import logging
from datetime import time as dt_time
from functools import wraps

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    jsonify,
)

from src.config import config
from src.database import get_db
from src.database import queries

logger = logging.getLogger(__name__)

bp = Blueprint("main", __name__)


def login_required(f):
    """Decorator to require login for routes."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)

    return decorated_function


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Login page for web admin panel."""
    if request.method == "POST":
        password = request.form.get("password", "")

        if password == config.WEB_ADMIN_PASSWORD:
            session["logged_in"] = True
            logger.info("Admin logged in to web panel")
            return redirect(url_for("main.dashboard"))
        else:
            logger.warning("Failed web panel login attempt")
            flash("Invalid password", "error")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    """Logout from web admin panel."""
    session.clear()
    return redirect(url_for("main.login"))


@bp.route("/")
@login_required
def dashboard():
    """Dashboard showing all 365 messages."""
    with get_db() as db:
        messages = queries.get_all_messages(db)
        return render_template("dashboard.html", messages=messages)


@bp.route("/message/<int:day>", methods=["GET", "POST"])
@login_required
def edit_message(day: int):
    """Edit message for a specific day."""
    # Validate day number
    if day < 1 or day > config.TOTAL_DAYS:
        flash("Invalid day number", "error")
        return redirect(url_for("main.dashboard"))

    with get_db() as db:
        message = queries.get_message_by_day(db, day)

        if request.method == "POST":
            content = request.form.get("content", "")
            send_time_str = request.form.get("send_time", "09:00")

            # Validate content length
            if len(content) > config.MAX_MESSAGE_LENGTH:
                flash(
                    f"Message too long. Maximum {config.MAX_MESSAGE_LENGTH} characters.",
                    "error",
                )
                return render_template(
                    "edit_message.html",
                    message=message,
                    day=day,
                    max_length=config.MAX_MESSAGE_LENGTH,
                )

            # Parse send time
            try:
                parts = send_time_str.split(":")
                send_time = dt_time(int(parts[0]), int(parts[1]))
            except (ValueError, IndexError):
                flash("Invalid time format. Use HH:MM.", "error")
                return render_template(
                    "edit_message.html",
                    message=message,
                    day=day,
                    max_length=config.MAX_MESSAGE_LENGTH,
                )

            # Update message
            queries.update_message(db, day, content, send_time)
            logger.info(f"Day {day} message updated via web panel")
            flash("Message saved successfully!", "success")
            return redirect(url_for("main.dashboard"))

        return render_template(
            "edit_message.html",
            message=message,
            day=day,
            max_length=config.MAX_MESSAGE_LENGTH,
        )


@bp.route("/message/<int:day>/preview")
@login_required
def preview_message(day: int):
    """AJAX endpoint to preview a message."""
    content = request.args.get("content", "")
    return jsonify({"preview": content})


@bp.route("/welcome", methods=["GET", "POST"])
@login_required
def edit_welcome():
    """Edit welcome message."""
    with get_db() as db:
        if request.method == "POST":
            content = request.form.get("content", "")

            # Validate content length
            if len(content) > config.MAX_MESSAGE_LENGTH:
                flash(
                    f"Message too long. Maximum {config.MAX_MESSAGE_LENGTH} characters.",
                    "error",
                )
                return render_template(
                    "edit_welcome.html",
                    content=content,
                    max_length=config.MAX_MESSAGE_LENGTH,
                )

            queries.set_welcome_message(db, content)
            logger.info("Welcome message updated via web panel")
            flash("Welcome message saved successfully!", "success")
            return redirect(url_for("main.dashboard"))

        welcome = queries.get_welcome_message(db)
        return render_template(
            "edit_welcome.html",
            content=welcome,
            max_length=config.MAX_MESSAGE_LENGTH,
        )
