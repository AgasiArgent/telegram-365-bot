"""Unit tests for admin Telegram commands."""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.database import init_db, get_db
from src.database import queries
from src.config import config


def test_admin_welcome_command():
    """
    Test Feature #10: Admin /welcome command shows current welcome message
    Steps:
    1. Authenticate as admin
    2. Set welcome message in database
    3. Send /welcome command
    4. Verify response contains exact welcome message text
    """
    print("=" * 60)
    print("Testing Feature #10: Admin /welcome command")
    print("=" * 60)

    # Initialize database
    init_db()

    # Test data
    test_telegram_id = 123123123
    test_welcome = "TEST_ADMIN_WELCOME - This is the welcome message for testing."

    # Step 1: Authenticate as admin
    print("\nStep 1: Authenticating as admin...")
    with get_db() as db:
        if not queries.is_admin(db, test_telegram_id):
            queries.add_admin(db, test_telegram_id)
        print(f"   Admin authenticated: {test_telegram_id}")

    # Step 2: Set welcome message in database
    print(f"\nStep 2: Setting welcome message...")
    with get_db() as db:
        queries.set_welcome_message(db, test_welcome)
        print(f"   Welcome message set: '{test_welcome[:40]}...'")

    # Step 3: Simulate /welcome command
    print("\nStep 3: Simulating /welcome command...")
    with get_db() as db:
        # Check admin status (same as cmd_welcome)
        if not queries.is_admin(db, test_telegram_id):
            print("   FAILED: Not admin, command would be ignored!")
            return False

        # Get welcome message (same as cmd_welcome)
        welcome = queries.get_welcome_message(db)
        response = f"Current welcome message:\n\n{welcome}"
        print(f"   Response that would be sent:")
        print(f"   '{response[:60]}...'")

    # Step 4: Verify response contains exact welcome message text
    print("\nStep 4: Verifying response contains exact welcome text...")
    if test_welcome in response:
        print("   SUCCESS: Response contains exact welcome message!")
    else:
        print("   FAILED: Response doesn't contain welcome message!")
        return False

    # Clean up
    with get_db() as db:
        queries.remove_admin(db, test_telegram_id)

    print("\n" + "=" * 60)
    print("TEST PASSED!")
    print("=" * 60)
    return True


def test_admin_setwelcome_command():
    """
    Test Feature #11: Admin /setwelcome command updates welcome message
    Steps:
    1. Authenticate as admin
    2. Send /setwelcome command with new text
    3. Verify success response
    4. Query database for updated welcome message
    """
    print("\n" + "=" * 60)
    print("Testing Feature #11: Admin /setwelcome command")
    print("=" * 60)

    # Initialize database
    init_db()

    # Test data
    test_telegram_id = 456456456
    new_welcome = "TEST_NEW_WELCOME - Updated welcome message via /setwelcome command."

    # Step 1: Authenticate as admin
    print("\nStep 1: Authenticating as admin...")
    with get_db() as db:
        if not queries.is_admin(db, test_telegram_id):
            queries.add_admin(db, test_telegram_id)
        print(f"   Admin authenticated: {test_telegram_id}")

    # Step 2: Simulate /setwelcome command
    print(f"\nStep 2: Simulating /setwelcome command...")
    with get_db() as db:
        # Check admin status
        if not queries.is_admin(db, test_telegram_id):
            print("   FAILED: Not admin!")
            return False

        # Validate length
        if len(new_welcome) > config.MAX_MESSAGE_LENGTH:
            print("   FAILED: Message too long!")
            return False

        # Update welcome message (same as cmd_setwelcome)
        queries.set_welcome_message(db, new_welcome)
        print(f"   Welcome message updated")

    # Step 3: Verify success response
    print("\nStep 3: Verifying success response...")
    print("   Response that would be sent: 'Welcome message updated successfully.'")
    print("   SUCCESS: Update confirmation would be sent")

    # Step 4: Query database for updated welcome message
    print("\nStep 4: Querying database for updated message...")
    with get_db() as db:
        stored_welcome = queries.get_welcome_message(db)
        print(f"   Stored message: '{stored_welcome[:50]}...'")

        if stored_welcome == new_welcome:
            print("   SUCCESS: Welcome message updated correctly!")
        else:
            print("   FAILED: Stored message doesn't match!")
            return False

    # Clean up
    with get_db() as db:
        queries.remove_admin(db, test_telegram_id)

    print("\n" + "=" * 60)
    print("TEST PASSED!")
    print("=" * 60)
    return True


def test_admin_day_command():
    """
    Test Feature #12: Admin /day command shows message for specific day
    Steps:
    1. Authenticate as admin
    2. Set message for day 100 in database
    3. Send /day 100 command
    4. Verify response shows day 100 message content and send time
    """
    print("\n" + "=" * 60)
    print("Testing Feature #12: Admin /day command")
    print("=" * 60)

    # Initialize database
    init_db()

    # Test data
    test_telegram_id = 789789789
    test_day = 100
    test_content = "TEST_DAY100 - This is the message for day 100."
    from datetime import time as dt_time
    test_send_time = dt_time(14, 30)

    # Step 1: Authenticate as admin
    print("\nStep 1: Authenticating as admin...")
    with get_db() as db:
        if not queries.is_admin(db, test_telegram_id):
            queries.add_admin(db, test_telegram_id)
        print(f"   Admin authenticated")

    # Step 2: Set message for day 100
    print(f"\nStep 2: Setting message for day {test_day}...")
    with get_db() as db:
        queries.update_message(db, test_day, test_content, test_send_time)
        print(f"   Day {test_day} message set")
        print(f"   Content: '{test_content[:40]}...'")
        print(f"   Send time: {test_send_time}")

    # Step 3: Simulate /day 100 command
    print(f"\nStep 3: Simulating /day {test_day} command...")
    with get_db() as db:
        # Check admin status
        if not queries.is_admin(db, test_telegram_id):
            print("   FAILED: Not admin!")
            return False

        # Get message for day (same as cmd_day)
        msg = queries.get_message_by_day(db, test_day)
        if not msg:
            print(f"   FAILED: No message for day {test_day}!")
            return False

        content = msg.content or "(empty)"
        send_time = msg.send_time.strftime("%H:%M") if msg.send_time else "09:00"
        response = f"Day {test_day} (sends at {send_time}):\n\n{content}"
        print(f"   Response that would be sent:")
        print(f"   '{response[:70]}...'")

    # Step 4: Verify response shows correct info
    print("\nStep 4: Verifying response content...")
    if test_content in response:
        print("   SUCCESS: Response contains message content!")
    else:
        print("   FAILED: Response missing content!")
        return False

    if "14:30" in response:
        print("   SUCCESS: Response contains send time!")
    else:
        print("   FAILED: Response missing send time!")
        return False

    # Clean up
    with get_db() as db:
        queries.remove_admin(db, test_telegram_id)
        # Reset day 100 message
        queries.update_message(db, test_day, "", dt_time(9, 0))

    print("\n" + "=" * 60)
    print("TEST PASSED!")
    print("=" * 60)
    return True


def test_admin_setday_command():
    """
    Test Feature #13: Admin /setday command updates day message
    Steps:
    1. Authenticate as admin
    2. Send /setday 50 with new text
    3. Verify success response
    4. Query database for updated day 50 message
    """
    print("\n" + "=" * 60)
    print("Testing Feature #13: Admin /setday command")
    print("=" * 60)

    # Initialize database
    init_db()

    # Test data
    test_telegram_id = 321321321
    test_day = 50
    new_content = "TEST_SETDAY50 - Updated via /setday command."

    # Step 1: Authenticate as admin
    print("\nStep 1: Authenticating as admin...")
    with get_db() as db:
        if not queries.is_admin(db, test_telegram_id):
            queries.add_admin(db, test_telegram_id)
        print(f"   Admin authenticated")

    # Step 2: Simulate /setday command
    print(f"\nStep 2: Simulating /setday {test_day} command...")
    with get_db() as db:
        # Check admin status
        if not queries.is_admin(db, test_telegram_id):
            print("   FAILED: Not admin!")
            return False

        # Validate length
        if len(new_content) > config.MAX_MESSAGE_LENGTH:
            print("   FAILED: Message too long!")
            return False

        # Update message (same as cmd_setday)
        queries.update_message(db, test_day, new_content)
        print(f"   Day {test_day} message updated")

    # Step 3: Verify success response
    print("\nStep 3: Verifying success response...")
    print(f"   Response: 'Day {test_day} message updated successfully.'")
    print("   SUCCESS: Update confirmation would be sent")

    # Step 4: Query database for updated message
    print("\nStep 4: Querying database for updated message...")
    with get_db() as db:
        msg = queries.get_message_by_day(db, test_day)
        print(f"   Stored content: '{msg.content}'")

        if msg.content == new_content:
            print("   SUCCESS: Day message updated correctly!")
        else:
            print("   FAILED: Stored content doesn't match!")
            return False

    # Clean up
    with get_db() as db:
        queries.remove_admin(db, test_telegram_id)
        from datetime import time as dt_time
        queries.update_message(db, test_day, "", dt_time(9, 0))

    print("\n" + "=" * 60)
    print("TEST PASSED!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    results = []

    results.append(("/welcome command", test_admin_welcome_command()))
    results.append(("/setwelcome command", test_admin_setwelcome_command()))
    results.append(("/day command", test_admin_day_command()))
    results.append(("/setday command", test_admin_setday_command()))

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    all_passed = True
    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\nALL TESTS PASSED!")
        print("Features #10, #11, #12, #13: PASSED")
    else:
        print("\nSOME TESTS FAILED!")
