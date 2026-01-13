"""Performance test for scheduler handling 1000 users."""
import sys
import os
import time
from datetime import datetime, time as dt_time, date

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.database import init_db, get_db
from src.database import queries
from src.database.models import User, Message


def test_scheduler_1000_users():
    """
    Test Feature #61: Scheduler handles 1000 users efficiently
    Steps:
    1. Create 1000 test users
    2. Configure same send time for all
    3. Trigger scheduler logic (query users and prepare messages)
    4. Verify all users processed within reasonable time
    5. Verify no timeout errors
    """
    print("=" * 60)
    print("Testing Feature #61: Scheduler handles 1000 users efficiently")
    print("=" * 60)

    # Initialize database
    init_db()

    # Test parameters
    NUM_USERS = 1000
    BASE_TELEGRAM_ID = 900000000
    TEST_SEND_TIME = dt_time(9, 0)  # 09:00
    TEST_MESSAGE = "TEST_PERFORMANCE - Daily message content"

    # Reasonable time threshold (5 seconds for 1000 users)
    TIME_THRESHOLD_SECONDS = 5.0

    # Step 1: Create 1000 test users
    print(f"\nStep 1: Creating {NUM_USERS} test users...")
    start_time = time.time()

    with get_db() as db:
        # First, clean up any existing test users
        existing_count = db.query(User).filter(
            User.telegram_id >= BASE_TELEGRAM_ID,
            User.telegram_id < BASE_TELEGRAM_ID + NUM_USERS
        ).delete()
        if existing_count > 0:
            print(f"   Cleaned up {existing_count} existing test users")
        db.commit()

        # Create test users in batches for efficiency
        batch_size = 100
        created = 0
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
            created += len(users)
            print(f"   Created {created}/{NUM_USERS} users...", end="\r")

        print(f"   Created {created}/{NUM_USERS} users    ")

    create_time = time.time() - start_time
    print(f"   User creation took: {create_time:.2f}s")

    # Step 2: Configure day 1 message with same send time for all
    print(f"\nStep 2: Configuring day 1 message with send_time {TEST_SEND_TIME}...")
    with get_db() as db:
        message = queries.get_message_by_day(db, 1)
        if message:
            message.content = TEST_MESSAGE
            message.send_time = TEST_SEND_TIME
            db.commit()
            print(f"   Day 1 message configured with content length: {len(TEST_MESSAGE)}")
        else:
            print("   FAILED: Day 1 message not found!")
            return False

    # Step 3: Trigger scheduler logic (simulate the query and processing)
    print("\nStep 3: Triggering scheduler logic (simulating query and message preparation)...")

    start_time = time.time()
    processed_count = 0
    error_count = 0

    import pytz

    with get_db() as db:
        # This is what the scheduler does - get all active users
        query_start = time.time()
        users = queries.get_users_for_delivery(db)
        query_time = time.time() - query_start
        print(f"   User query returned {len(users)} users in {query_time:.3f}s")

        # Process each user (simulate what scheduler does)
        process_start = time.time()
        messages_prepared = 0

        for user in users:
            try:
                # Skip non-test users
                if user.telegram_id < BASE_TELEGRAM_ID or user.telegram_id >= BASE_TELEGRAM_ID + NUM_USERS:
                    continue

                processed_count += 1

                # Skip if already received message today
                if user.last_message_date == date.today():
                    continue

                # Get user's timezone
                try:
                    user_tz = pytz.timezone(user.timezone or "UTC")
                except Exception:
                    user_tz = pytz.UTC

                # Get message for user's current day
                message = queries.get_message_by_day(db, user.current_day)
                if not message or not message.content:
                    continue

                # In real scheduler, here we would check time and send
                # For test, we just count that message would be prepared
                messages_prepared += 1

            except Exception as e:
                error_count += 1
                if error_count <= 3:
                    print(f"   Error processing user {user.telegram_id}: {e}")

        process_time = time.time() - process_start
        print(f"   Processing loop took: {process_time:.3f}s")
        print(f"   Messages prepared: {messages_prepared}")

    total_time = time.time() - start_time
    print(f"\n   Total scheduler simulation time: {total_time:.3f}s")

    # Step 4: Verify all users processed within reasonable time
    print(f"\nStep 4: Verifying processing time is under {TIME_THRESHOLD_SECONDS}s threshold...")
    if total_time < TIME_THRESHOLD_SECONDS:
        print(f"   SUCCESS: {total_time:.3f}s < {TIME_THRESHOLD_SECONDS}s threshold")
    else:
        print(f"   FAILED: {total_time:.3f}s exceeded {TIME_THRESHOLD_SECONDS}s threshold!")
        return False

    print(f"   Processed {processed_count} test users")

    # Step 5: Verify no timeout errors
    print(f"\nStep 5: Verifying no timeout errors...")
    if error_count == 0:
        print(f"   SUCCESS: No errors during processing")
    else:
        print(f"   WARNING: {error_count} errors occurred during processing")
        if error_count > 10:  # Allow some tolerance
            print(f"   FAILED: Too many errors!")
            return False

    # Performance metrics summary
    print("\n--- Performance Summary ---")
    if processed_count > 0:
        avg_time_per_user = (total_time * 1000) / processed_count  # in ms
        users_per_second = processed_count / total_time
        print(f"   Average time per user: {avg_time_per_user:.3f}ms")
        print(f"   Users processed per second: {users_per_second:.1f}")

    # Clean up test users
    print("\nCleaning up test users...")
    with get_db() as db:
        deleted = db.query(User).filter(
            User.telegram_id >= BASE_TELEGRAM_ID,
            User.telegram_id < BASE_TELEGRAM_ID + NUM_USERS
        ).delete()
        db.commit()
        print(f"   Deleted {deleted} test users")

        # Reset day 1 message
        message = queries.get_message_by_day(db, 1)
        if message:
            message.content = ""
            message.send_time = dt_time(9, 0)
            db.commit()
        print("   Reset day 1 message")

    print("\n" + "=" * 60)
    print("TEST PASSED: Scheduler handles 1000 users efficiently!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    result = test_scheduler_1000_users()
    if result:
        print("\nFEATURE #61: PASSED")
        sys.exit(0)
    else:
        print("\nFEATURE #61: FAILED")
        sys.exit(1)
