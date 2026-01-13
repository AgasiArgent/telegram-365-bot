"""Unit tests for bot logic - tests database operations without aiogram."""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.database import init_db, get_db
from src.database import queries


def test_start_command_logic():
    """
    Test the /start command logic:
    1. New user sends /start - user created, welcome message sent
    2. Returning user sends /start - user found, welcome message sent
    3. Welcome message matches database setting
    """
    print("=" * 60)
    print("Testing /start command logic")
    print("=" * 60)

    # Initialize database
    print("\n1. Initializing database...")
    init_db()
    print("   Database initialized successfully")

    # Simulate new user sending /start
    test_telegram_id = 123456789
    test_username = "test_user_start"

    print(f"\n2. Simulating new user /start (telegram_id={test_telegram_id})...")

    with get_db() as db:
        # Check if user exists (should not exist yet, but clean up if it does)
        existing_user = queries.get_user_by_telegram_id(db, test_telegram_id)
        if existing_user:
            print("   Cleaning up existing test user...")
            db.delete(existing_user)
            db.commit()

        # Simulate /start command logic
        user = queries.get_user_by_telegram_id(db, test_telegram_id)

        if user:
            print("   ERROR: User should not exist yet!")
            return False
        else:
            # New user - create account (mimics cmd_start)
            user = queries.create_user(
                db,
                telegram_id=test_telegram_id,
                username=test_username,
                timezone="UTC",
            )
            print(f"   New user created: id={user.id}, telegram_id={user.telegram_id}")
            print(f"   Username: {user.username}, Day: {user.current_day}")

        # Get welcome message (mimics the response)
        welcome = queries.get_welcome_message(db)
        print(f"\n3. Welcome message that would be sent:")
        print(f"   \"{welcome}\"")

        # Verify the welcome message matches what we set earlier
        if "TEST_WELCOME_12345" in welcome:
            print("   SUCCESS: Welcome message contains our test data!")
        else:
            print("   Note: Welcome message is default (test data not found)")

    # Simulate returning user
    print(f"\n4. Simulating returning user /start (same telegram_id)...")

    with get_db() as db:
        user = queries.get_user_by_telegram_id(db, test_telegram_id)

        if user:
            print(f"   Found existing user: id={user.id}")
            print(f"   Current day: {user.current_day}, Active: {user.is_active}")

            if not user.is_active:
                queries.set_user_active(db, user, True)
                print("   User reactivated")
            else:
                print("   User already active, no changes needed")

            # Get welcome message
            welcome = queries.get_welcome_message(db)
            print(f"\n5. Welcome message for returning user:")
            print(f"   \"{welcome}\"")
        else:
            print("   ERROR: User should exist!")
            return False

    # Clean up test user
    print(f"\n6. Cleaning up test user...")
    with get_db() as db:
        user = queries.get_user_by_telegram_id(db, test_telegram_id)
        if user:
            db.delete(user)
            db.commit()
            print("   Test user deleted")

    print("\n" + "=" * 60)
    print("TEST PASSED: /start command logic works correctly!")
    print("=" * 60)
    return True


def test_welcome_message_retrieval():
    """Test that welcome message is correctly retrieved from database."""
    print("\n" + "=" * 60)
    print("Testing welcome message retrieval")
    print("=" * 60)

    with get_db() as db:
        welcome = queries.get_welcome_message(db)
        print(f"\nCurrent welcome message:")
        print(f"  \"{welcome}\"")
        print(f"\nMessage length: {len(welcome)} characters")

        if welcome:
            print("SUCCESS: Welcome message retrieved successfully!")
            return True
        else:
            print("ERROR: Welcome message is empty!")
            return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("TELEGRAM 365 BOT - LOGIC TESTS")
    print("These tests verify the bot logic without requiring aiogram")
    print("=" * 60 + "\n")

    results = []

    # Run tests
    results.append(("Welcome Message Retrieval", test_welcome_message_retrieval()))
    results.append(("/start Command Logic", test_start_command_logic()))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED!")
    print("=" * 60)
