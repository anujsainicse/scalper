#!/usr/bin/env python3
"""
Quick migration script to add cancellation_reason column to orders table

Run this before starting the backend server after pulling the latest changes.

Usage:
    python run_migration.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import AsyncSessionLocal
from sqlalchemy import text


async def run_migration():
    """Add cancellation_reason column to orders table"""

    print("🔄 Running database migration...")
    print("   Adding cancellation_reason column to orders table")

    try:
        async with AsyncSessionLocal() as db:
            # Check if column already exists
            check_query = text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'orders'
                AND column_name = 'cancellation_reason';
            """)

            result = await db.execute(check_query)
            existing = result.fetchone()

            if existing:
                print("ℹ️  Column already exists - skipping migration")
                return True

            # Add the column
            migration_query = text("""
                ALTER TABLE orders
                ADD COLUMN cancellation_reason VARCHAR(50);
            """)

            await db.execute(migration_query)
            await db.commit()

            print("✅ Migration completed successfully!")
            print("   Column 'cancellation_reason' added to 'orders' table")

            # Verify the column was added
            verify_result = await db.execute(check_query)
            if verify_result.fetchone():
                print("✅ Verification passed - column exists in database")
                return True
            else:
                print("❌ Verification failed - column not found after migration")
                return False

    except Exception as e:
        print(f"❌ Migration failed with error:")
        print(f"   {type(e).__name__}: {e}")
        print()
        print("💡 Troubleshooting:")
        print("   1. Make sure PostgreSQL is running")
        print("   2. Check DATABASE_URL in .env file")
        print("   3. Verify database 'scalper_bot' exists")
        print("   4. Try running SQL manually:")
        print("      psql scalper_bot -c \"ALTER TABLE orders ADD COLUMN cancellation_reason VARCHAR(50);\"")
        return False


def main():
    """Main entry point"""
    print()
    print("=" * 70)
    print("  Database Migration: Add cancellation_reason to orders")
    print("=" * 70)
    print()

    success = asyncio.run(run_migration())

    print()
    if success:
        print("🎉 All done! You can now start the backend server.")
    else:
        print("⚠️  Migration failed. Please fix the error and try again.")
    print()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
