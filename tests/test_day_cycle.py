"""Unit tests for day 365 cycle reset."""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.database import init_db, get_db
from src.database import queries
from src.database.models import User
from src.config import config


def test_day_cycle():
    """
    Test Feature #7: Day 365 cycles back to day 1
    Steps:
    1. Set user current_day to 365
    2. Trigger message delivery for day 365
    3. Verify current_day is now 1
    4. Verify cycle continues correctly
    """
    print("=" * 60)
    print("Testing Feature #7: Day 365 cycles back to day 1")
    print("=" * 60)

    # Initialize database
    init_db()

    # Test data
    test_telegram_id = 444555666
    final_day = config.TOTAL_DAYS  # 365

    # Clean up
    with get_db() as db:
        existing = queries.get_user_by_telegram_id(db, test_telegram_id)
        if existing:
            db.delete(existing)
            db.commit()

    # Step 1: Set user current_day to 365
    print(f"\nStep 1: Setting user current_day to {final_day}...")
    with get_db() as db:
        user = User(
            telegram_id=test_telegram_id,
            username="cycle_test_user",
            timezone="UTC",
            current_day=final_day,
            is_active=True,
            last_message_date=None,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"   User created: current_day={user.current_day}")
        print(f"   TOTAL_DAYS configured as: {config.TOTAL_DAYS}")

    # Step 2: Trigger message delivery (simulate)
    print(f"\nStep 2: Simulating message delivery for day {final_day}...")
    with get_db() as db:
        user = queries.get_user_by_telegram_id(db, test_telegram_id)
        old_day = user.current_day
        print(f"   Before: current_day={old_day}")

        # This should cycle back to 1
        queries.update_user_day(db, user)
        print("   update_user_day() called")

    # Step 3: Verify current_day is now 1
    print("\nStep 3: Verifying current_day is now 1...")
    with get_db() as db:
        user = queries.get_user_by_telegram_id(db, test_telegram_id)
        print(f"   Expected: 1 (cycle reset)")
        print(f"   Actual: {user.current_day}")

        if user.current_day != 1:
            print(f"   FAILED: current_day should cycle back to 1 after {final_day}!")
            return False
        print("   SUCCESS: Day cycle works correctly - reset to day 1!")

    # Step 4: Verify cycle continues correctly (from 1 to 2)
    print("\nStep 4: Verifying cycle continues correctly (1 -> 2)...")
    with get_db() as db:
        user = queries.get_user_by_telegram_id(db, test_telegram_id)
        # Reset last_message_date to allow another update
        user.last_message_date = None
        db.commit()

        queries.update_user_day(db, user)

        user = queries.get_user_by_telegram_id(db, test_telegram_id)
        print(f"   After another delivery: current_day={user.current_day}")

        if user.current_day != 2:
            print("   FAILED: Day should continue to 2!")
            return False
        print("   SUCCESS: Cycle continues normally after reset")

    # Clean up
    print("\nCleaning up...")
    with get_db() as db:
        user = queries.get_user_by_telegram_id(db, test_telegram_id)
        if user:
            db.delete(user)
            db.commit()
        print("   Test user deleted")

    print("\n" + "=" * 60)
    print("TEST PASSED: Day 365 cycle reset works correctly!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    result = test_day_cycle()
    if result:
        print("\nFEATURE #7: PASSED")
    else:
        print("\nFEATURE #7: FAILED")
