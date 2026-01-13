"""Unit tests for day increment logic."""
import sys
import os
from datetime import date

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.database import init_db, get_db
from src.database import queries
from src.database.models import User


def test_day_increment():
    """
    Test Feature #6: User day increments after receiving message
    Steps:
    1. Set user current_day to 50
    2. Trigger message delivery for day 50
    3. Verify current_day is now 51
    4. Verify last_message_date is updated
    """
    print("=" * 60)
    print("Testing Feature #6: User day increments after receiving message")
    print("=" * 60)

    # Initialize database
    init_db()

    # Test data
    test_telegram_id = 111222333
    target_day = 50

    # Clean up
    with get_db() as db:
        existing = queries.get_user_by_telegram_id(db, test_telegram_id)
        if existing:
            db.delete(existing)
            db.commit()

    # Step 1: Set user current_day to 50
    print(f"\nStep 1: Setting user current_day to {target_day}...")
    with get_db() as db:
        user = User(
            telegram_id=test_telegram_id,
            username="day_increment_test",
            timezone="UTC",
            current_day=target_day,
            is_active=True,
            last_message_date=None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"   User created: current_day={user.current_day}")

    # Step 2: Trigger message delivery (simulate)
    print(f"\nStep 2: Simulating message delivery for day {target_day}...")
    with get_db() as db:
        user = queries.get_user_by_telegram_id(db, test_telegram_id)
        old_day = user.current_day
        old_date = user.last_message_date
        print(f"   Before: current_day={old_day}, last_message_date={old_date}")

        # This is what happens after successful message send
        queries.update_user_day(db, user)
        print("   update_user_day() called")

    # Step 3: Verify current_day is now 51
    print(f"\nStep 3: Verifying current_day is now {target_day + 1}...")
    with get_db() as db:
        user = queries.get_user_by_telegram_id(db, test_telegram_id)
        print(f"   Expected: {target_day + 1}")
        print(f"   Actual: {user.current_day}")

        if user.current_day != target_day + 1:
            print(f"   FAILED: current_day should be {target_day + 1}!")
            return False
        print("   SUCCESS: current_day incremented correctly")

    # Step 4: Verify last_message_date is updated
    print("\nStep 4: Verifying last_message_date is updated...")
    with get_db() as db:
        user = queries.get_user_by_telegram_id(db, test_telegram_id)
        today = date.today()
        print(f"   Expected: {today}")
        print(f"   Actual: {user.last_message_date}")

        if user.last_message_date != today:
            print("   FAILED: last_message_date should be today!")
            return False
        print("   SUCCESS: last_message_date updated correctly")

    # Clean up
    print("\nCleaning up...")
    with get_db() as db:
        user = queries.get_user_by_telegram_id(db, test_telegram_id)
        if user:
            db.delete(user)
            db.commit()
        print("   Test user deleted")

    print("\n" + "=" * 60)
    print("TEST PASSED: Day increment logic works correctly!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    result = test_day_increment()
    if result:
        print("\nFEATURE #6: PASSED")
    else:
        print("\nFEATURE #6: FAILED")
