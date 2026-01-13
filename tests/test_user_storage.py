"""Unit tests for user storage - verifies user data is correctly stored."""
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


def test_new_user_storage():
    """
    Test Feature #2: New user stored in database on /start
    Steps:
    1. Send /start from new Telegram user
    2. Query database for user record
    3. Verify telegram_id is stored correctly
    4. Verify current_day is set to 1
    5. Verify is_active is true
    6. Verify started_at timestamp is set
    """
    print("=" * 60)
    print("Testing Feature #2: New user stored in database on /start")
    print("=" * 60)

    # Initialize database
    init_db()

    # Test data
    test_telegram_id = 987654321
    test_username = "test_new_user"

    # Clean up any existing test user
    with get_db() as db:
        existing = queries.get_user_by_telegram_id(db, test_telegram_id)
        if existing:
            db.delete(existing)
            db.commit()
            print("Cleaned up existing test user")

    # Step 1: Simulate /start from new user
    print("\nStep 1: Simulating /start from new Telegram user...")
    with get_db() as db:
        user = queries.create_user(
            db,
            telegram_id=test_telegram_id,
            username=test_username,
            timezone="UTC",
        )
        user_id = user.id
        print(f"   User created with id={user_id}")

    # Step 2: Query database for user record
    print("\nStep 2: Querying database for user record...")
    with get_db() as db:
        user = queries.get_user_by_telegram_id(db, test_telegram_id)

        if not user:
            print("   FAILED: User not found in database!")
            return False
        print(f"   SUCCESS: User found in database (id={user.id})")

        # Step 3: Verify telegram_id is stored correctly
        print(f"\nStep 3: Verifying telegram_id...")
        print(f"   Expected: {test_telegram_id}")
        print(f"   Actual: {user.telegram_id}")
        if user.telegram_id != test_telegram_id:
            print("   FAILED: telegram_id mismatch!")
            return False
        print("   SUCCESS: telegram_id stored correctly")

        # Step 4: Verify current_day is set to 1
        print(f"\nStep 4: Verifying current_day is set to 1...")
        print(f"   Expected: 1")
        print(f"   Actual: {user.current_day}")
        if user.current_day != 1:
            print("   FAILED: current_day should be 1!")
            return False
        print("   SUCCESS: current_day is 1")

        # Step 5: Verify is_active is true
        print(f"\nStep 5: Verifying is_active is True...")
        print(f"   Expected: True")
        print(f"   Actual: {user.is_active}")
        if not user.is_active:
            print("   FAILED: is_active should be True!")
            return False
        print("   SUCCESS: is_active is True")

        # Step 6: Verify started_at timestamp is set
        print(f"\nStep 6: Verifying started_at timestamp is set...")
        print(f"   started_at: {user.started_at}")
        if user.started_at is None:
            print("   FAILED: started_at is not set!")
            return False
        print("   SUCCESS: started_at timestamp is set")

        # Additional verification: username
        print(f"\n   Bonus - username: {user.username}")
        print(f"   Bonus - timezone: {user.timezone}")
        print(f"   Bonus - created_at: {user.created_at}")

    # Clean up test user
    print("\nCleaning up test user...")
    with get_db() as db:
        user = queries.get_user_by_telegram_id(db, test_telegram_id)
        if user:
            db.delete(user)
            db.commit()
            print("   Test user deleted")

    print("\n" + "=" * 60)
    print("TEST PASSED: All user storage verifications successful!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    result = test_new_user_storage()
    if result:
        print("\nFEATURE #2: PASSED")
    else:
        print("\nFEATURE #2: FAILED")
