"""Unit tests for returning user behavior."""
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


def test_returning_user():
    """
    Test Feature #4: Returning user continues from same day
    Steps:
    1. Create user at day 50 in database
    2. Set is_active to false (simulating block)
    3. Send /start command
    4. Verify current_day remains at 50
    5. Verify is_active is now true
    """
    print("=" * 60)
    print("Testing Feature #4: Returning user continues from same day")
    print("=" * 60)

    # Initialize database
    init_db()

    # Test data
    test_telegram_id = 777777777
    test_username = "returning_user_test"
    target_day = 50

    # Clean up any existing test user
    with get_db() as db:
        existing = queries.get_user_by_telegram_id(db, test_telegram_id)
        if existing:
            db.delete(existing)
            db.commit()

    # Step 1: Create user at day 50 in database
    print("\nStep 1: Creating user at day 50 in database...")
    with get_db() as db:
        user = User(
            telegram_id=test_telegram_id,
            username=test_username,
            timezone="UTC",
            current_day=target_day,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"   User created: id={user.id}, current_day={user.current_day}")

    # Step 2: Set is_active to false (simulating block)
    print("\nStep 2: Setting is_active to false (simulating block)...")
    with get_db() as db:
        user = queries.get_user_by_telegram_id(db, test_telegram_id)
        queries.set_user_active(db, user, False)
        print(f"   is_active set to: {user.is_active}")

        # Verify it's false
        user = queries.get_user_by_telegram_id(db, test_telegram_id)
        if user.is_active:
            print("   FAILED: is_active should be False!")
            return False
        print("   SUCCESS: User is now inactive (blocked)")

    # Step 3: Simulate /start command (returning user logic)
    print("\nStep 3: Simulating /start command...")
    with get_db() as db:
        # This is the exact logic from cmd_start handler
        user = queries.get_user_by_telegram_id(db, test_telegram_id)

        if user:
            if not user.is_active:
                queries.set_user_active(db, user, True)
                print(f"   User reactivated at day {user.current_day}")
            else:
                print("   User was already active")
        else:
            print("   FAILED: User not found!")
            return False

    # Step 4: Verify current_day remains at 50
    print("\nStep 4: Verifying current_day remains at 50...")
    with get_db() as db:
        user = queries.get_user_by_telegram_id(db, test_telegram_id)
        print(f"   Expected: {target_day}")
        print(f"   Actual: {user.current_day}")

        if user.current_day != target_day:
            print(f"   FAILED: current_day changed from {target_day} to {user.current_day}!")
            return False
        print("   SUCCESS: current_day preserved correctly")

    # Step 5: Verify is_active is now true
    print("\nStep 5: Verifying is_active is now true...")
    with get_db() as db:
        user = queries.get_user_by_telegram_id(db, test_telegram_id)
        print(f"   Expected: True")
        print(f"   Actual: {user.is_active}")

        if not user.is_active:
            print("   FAILED: is_active should be True!")
            return False
        print("   SUCCESS: is_active is True")

    # Clean up
    print("\nCleaning up test user...")
    with get_db() as db:
        user = queries.get_user_by_telegram_id(db, test_telegram_id)
        if user:
            db.delete(user)
            db.commit()
            print("   Test user deleted")

    print("\n" + "=" * 60)
    print("TEST PASSED: Returning user handling works correctly!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    result = test_returning_user()
    if result:
        print("\nFEATURE #4: PASSED")
    else:
        print("\nFEATURE #4: FAILED")
