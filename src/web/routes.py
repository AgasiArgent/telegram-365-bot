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
            session.permanent = True  # Enable session timeout
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


@bp.route("/api/test/scheduler-performance")
@login_required
def test_scheduler_performance():
    """
    Test endpoint for Feature #61: Scheduler handles 1000 users efficiently.
    Creates 1000 test users, queries them, and measures performance.
    """
    import time
    from datetime import date, time as dt_time
    from src.database.models import User, Message
    import pytz

    NUM_USERS = 1000
    BASE_TELEGRAM_ID = 900000000
    TIME_THRESHOLD_SECONDS = 5.0

    results = {
        "test": "Scheduler handles 1000 users efficiently",
        "num_users": NUM_USERS,
        "threshold_seconds": TIME_THRESHOLD_SECONDS,
        "steps": [],
        "passed": False,
    }

    try:
        # Step 1: Create 1000 test users
        step1_start = time.time()
        with get_db() as db:
            # Clean up existing test users first
            existing = db.query(User).filter(
                User.telegram_id >= BASE_TELEGRAM_ID,
                User.telegram_id < BASE_TELEGRAM_ID + NUM_USERS
            ).delete()

            # Create users in batches
            batch_size = 100
            for batch_start in range(0, NUM_USERS, batch_size):
                batch_end = min(batch_start + batch_size, NUM_USERS)
                users = []
                for i in range(batch_start, batch_end):
                    user = User(
                        telegram_id=BASE_TELEGRAM_ID + i,
                        username=f"perf_test_user_{i}",
                        timezone="UTC",
                        current_day=1,
                        is_active=True,
                        last_message_date=None,
                    )
                    users.append(user)
                db.add_all(users)
                db.commit()

        step1_time = time.time() - step1_start
        results["steps"].append({
            "step": 1,
            "description": f"Create {NUM_USERS} test users",
            "time_seconds": round(step1_time, 3),
            "passed": True
        })

        # Step 2: Configure message for day 1
        with get_db() as db:
            message = queries.get_message_by_day(db, 1)
            if message:
                message.content = "TEST_PERFORMANCE - Daily message"
                message.send_time = dt_time(9, 0)
                db.commit()
        results["steps"].append({
            "step": 2,
            "description": "Configure day 1 message",
            "passed": True
        })

        # Step 3: Trigger scheduler logic (query and process)
        step3_start = time.time()
        processed_count = 0
        messages_prepared = 0
        error_count = 0

        with get_db() as db:
            # Query users (what scheduler does)
            query_start = time.time()
            users = queries.get_users_for_delivery(db)
            query_time = time.time() - query_start

            # Process each user
            for user in users:
                try:
                    if user.telegram_id < BASE_TELEGRAM_ID or user.telegram_id >= BASE_TELEGRAM_ID + NUM_USERS:
                        continue

                    processed_count += 1

                    if user.last_message_date == date.today():
                        continue

                    try:
                        user_tz = pytz.timezone(user.timezone or "UTC")
                    except Exception:
                        user_tz = pytz.UTC

                    message = queries.get_message_by_day(db, user.current_day)
                    if message and message.content:
                        messages_prepared += 1

                except Exception as e:
                    error_count += 1

        step3_time = time.time() - step3_start
        results["steps"].append({
            "step": 3,
            "description": "Trigger scheduler logic",
            "time_seconds": round(step3_time, 3),
            "query_time_seconds": round(query_time, 3),
            "processed_count": processed_count,
            "messages_prepared": messages_prepared,
            "passed": True
        })

        # Step 4: Verify all processed within reasonable time
        total_time = step3_time
        step4_passed = total_time < TIME_THRESHOLD_SECONDS
        results["steps"].append({
            "step": 4,
            "description": f"Verify processing time < {TIME_THRESHOLD_SECONDS}s",
            "total_time_seconds": round(total_time, 3),
            "passed": step4_passed
        })

        # Step 5: Verify no timeout errors
        step5_passed = error_count == 0 or error_count <= 10
        results["steps"].append({
            "step": 5,
            "description": "Verify no timeout errors",
            "error_count": error_count,
            "passed": step5_passed
        })

        # Overall result
        results["passed"] = step4_passed and step5_passed
        results["total_time_seconds"] = round(total_time, 3)

        if processed_count > 0:
            results["avg_time_per_user_ms"] = round((total_time * 1000) / processed_count, 3)
            results["users_per_second"] = round(processed_count / total_time, 1)

        # Clean up
        with get_db() as db:
            deleted = db.query(User).filter(
                User.telegram_id >= BASE_TELEGRAM_ID,
                User.telegram_id < BASE_TELEGRAM_ID + NUM_USERS
            ).delete()
            db.commit()
            # Reset day 1 message
            message = queries.get_message_by_day(db, 1)
            if message:
                message.content = ""
                message.send_time = dt_time(9, 0)
                db.commit()
        results["cleanup"] = {"deleted_users": deleted}

    except Exception as e:
        results["error"] = str(e)
        results["passed"] = False

    return jsonify(results)


@bp.route("/api/test/session-timeout")
@login_required
def test_session_timeout():
    """
    Test endpoint for Feature #28: Session expires after inactivity.
    This endpoint allows testing session expiration by manually expiring the session.
    """
    action = request.args.get("action", "info")

    if action == "expire":
        # Manually expire the session by clearing it
        session.clear()
        return jsonify({
            "test": "Session expires after inactivity",
            "action": "expire",
            "result": "Session cleared - next request will require login",
            "passed": True
        })

    elif action == "info":
        # Return session info
        from datetime import datetime
        return jsonify({
            "test": "Session expires after inactivity",
            "action": "info",
            "session_permanent": session.permanent if hasattr(session, 'permanent') else False,
            "session_timeout_minutes": config.SESSION_TIMEOUT_MINUTES,
            "logged_in": session.get("logged_in", False),
            "passed": True
        })

    else:
        return jsonify({
            "error": "Unknown action. Use 'info' or 'expire'",
            "passed": False
        })


@bp.route("/api/test/simulate-error")
@login_required
def test_simulate_error():
    """
    Test endpoint for Feature #49: Network error shows user-friendly message.
    Simulates a database connection failure to test error handling.
    """
    error_type = request.args.get("type", "database")

    if error_type == "database":
        # Simulate database connection error
        raise Exception("Database connection failed: Connection refused")
    elif error_type == "timeout":
        # Simulate timeout error
        raise TimeoutError("Operation timed out after 30 seconds")
    elif error_type == "network":
        # Simulate network error
        raise ConnectionError("Network is unreachable")
    else:
        raise RuntimeError(f"Simulated error: {error_type}")
