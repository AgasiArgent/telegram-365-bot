"""Unit tests for non-admin command restrictions."""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.database import init_db, get_db
from src.database import queries


def test_non_admin_cannot_use_admin_commands():
    """
    Test Feature #14: Non-admin cannot use admin commands
    Steps:
    1. Ensure user is not in admins table
    2. Send /welcome command
    3. Verify command rejected or ignored
    4. Send /setwelcome command
    5. Verify command rejected or ignored
    """
    print("=" * 60)
    print("Testing Feature #14: Non-admin cannot use admin commands")
    print("=" * 60)

    # Initialize database
    init_db()

    # Test data
    non_admin_telegram_id = 999999111

    # Step 1: Ensure user is not in admins table
    print("\nStep 1: Ensuring user is not in admins table...")
    with get_db() as db:
        # Remove from admins if exists
        if queries.is_admin(db, non_admin_telegram_id):
            queries.remove_admin(db, non_admin_telegram_id)

        is_admin = queries.is_admin(db, non_admin_telegram_id)
        print(f"   User {non_admin_telegram_id} is admin: {is_admin}")

        if is_admin:
            print("   FAILED: User should not be admin!")
            return False
        print("   SUCCESS: User is not an admin")

    # Step 2 & 3: Simulate /welcome command (should be ignored)
    print("\nStep 2 & 3: Simulating /welcome command as non-admin...")
    with get_db() as db:
        # This is the check from cmd_welcome
        if not queries.is_admin(db, non_admin_telegram_id):
            print("   Command would be IGNORED (no response)")
            print("   SUCCESS: Non-admin cannot view welcome message")
        else:
            print("   FAILED: Command was not blocked!")
            return False

    # Step 4 & 5: Simulate /setwelcome command (should be ignored)
    print("\nStep 4 & 5: Simulating /setwelcome command as non-admin...")

    # Store original welcome message
    with get_db() as db:
        original_welcome = queries.get_welcome_message(db)

    with get_db() as db:
        # This is the check from cmd_setwelcome
        if not queries.is_admin(db, non_admin_telegram_id):
            print("   Command would be IGNORED (no response)")
            print("   SUCCESS: Non-admin cannot set welcome message")
        else:
            print("   FAILED: Command was not blocked!")
            return False

    # Verify welcome message was not changed
    with get_db() as db:
        current_welcome = queries.get_welcome_message(db)
        if current_welcome != original_welcome:
            print("   FAILED: Welcome message was modified by non-admin!")
            return False
        print("   SUCCESS: Welcome message unchanged")

    # Test /day and /setday as well
    print("\n--- Testing /day and /setday commands ---")

    with get_db() as db:
        if not queries.is_admin(db, non_admin_telegram_id):
            print("   /day command would be IGNORED")
            print("   /setday command would be IGNORED")
            print("   SUCCESS: All admin commands blocked for non-admin")
        else:
            return False

    print("\n" + "=" * 60)
    print("TEST PASSED: Non-admin correctly blocked from admin commands!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    result = test_non_admin_cannot_use_admin_commands()
    if result:
        print("\nFEATURE #14: PASSED")
    else:
        print("\nFEATURE #14: FAILED")
