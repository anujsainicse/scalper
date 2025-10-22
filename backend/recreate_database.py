#!/usr/bin/env python3
"""
Recreate Database Script

This script will:
1. Drop the existing scalper_bot database (if it exists)
2. Create a fresh scalper_bot database
3. Create all tables with the latest schema (including cancellation_reason)
4. Verify the setup

WARNING: This will DELETE ALL DATA in the scalper_bot database!

Usage:
    python recreate_database.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


async def recreate_database():
    """Drop and recreate the database with all tables"""

    print()
    print("=" * 80)
    print("  DATABASE RECREATION - This will DELETE ALL DATA!")
    print("=" * 80)
    print()

    # Get confirmation
    response = input("Are you sure you want to DROP the scalper_bot database? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Aborted by user")
        return False

    print()
    print("🔄 Starting database recreation process...")
    print()

    try:
        # Import after confirmation to avoid loading models unnecessarily
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        from app.models.bot import Base  # This imports all models

        # Step 1: Connect to postgres database (not scalper_bot) to drop/create
        print("📍 Step 1: Connecting to PostgreSQL server...")
        # Use current system user for macOS PostgreSQL default setup
        import os
        db_user = os.getenv("USER", "postgres")
        postgres_url = f"postgresql+asyncpg://{db_user}@localhost:5432/postgres"
        print(f"   Using database user: {db_user}")
        admin_engine = create_async_engine(postgres_url, isolation_level="AUTOCOMMIT")

        async with admin_engine.connect() as conn:
            # Drop existing database
            print("🗑️  Step 2: Dropping existing 'scalper_bot' database...")
            try:
                await conn.execute(text("DROP DATABASE IF EXISTS scalper_bot;"))
                print("   ✅ Database dropped successfully")
            except Exception as e:
                print(f"   ⚠️  Warning: {e}")

            # Create fresh database
            print("🏗️  Step 3: Creating new 'scalper_bot' database...")
            await conn.execute(text("CREATE DATABASE scalper_bot;"))
            print("   ✅ Database created successfully")

        await admin_engine.dispose()
        print()

        # Step 2: Connect to new database and create tables
        print("📍 Step 4: Connecting to new 'scalper_bot' database...")
        app_url = f"postgresql+asyncpg://{db_user}@localhost:5432/scalper_bot"
        app_engine = create_async_engine(app_url)

        print("🏗️  Step 5: Creating all tables with latest schema...")
        async with app_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("   ✅ All tables created successfully")
        print()

        # Step 3: Verify tables
        print("✅ Step 6: Verifying table creation...")
        async with app_engine.connect() as conn:
            # Check tables exist
            result = await conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]

            print(f"   📋 Tables created: {', '.join(tables)}")

            expected_tables = ['bots', 'orders', 'activity_logs', 'telegram_connections']
            missing = [t for t in expected_tables if t not in tables]
            if missing:
                print(f"   ⚠️  Warning: Missing tables: {', '.join(missing)}")

            # Verify cancellation_reason column exists
            result = await conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'orders' AND column_name = 'cancellation_reason';
            """))
            if result.fetchone():
                print("   ✅ cancellation_reason column exists in orders table")
            else:
                print("   ❌ ERROR: cancellation_reason column NOT found!")
                return False

            # Show orders table structure
            print()
            print("📋 Orders table structure:")
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'orders'
                ORDER BY ordinal_position;
            """))
            for row in result.fetchall():
                nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                print(f"   - {row[0]:<25} {row[1]:<20} {nullable}")

        await app_engine.dispose()

        print()
        print("=" * 80)
        print("  ✅ DATABASE RECREATION COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        print("📝 Summary:")
        print("   - Old database: DROPPED")
        print("   - New database: CREATED")
        print("   - Tables: CREATED with latest schema")
        print("   - cancellation_reason: INCLUDED in orders table")
        print()
        print("🚀 You can now start the backend server:")
        print("   uvicorn app.main:app --reload")
        print()

        return True

    except Exception as e:
        print()
        print("=" * 80)
        print("  ❌ DATABASE RECREATION FAILED!")
        print("=" * 80)
        print()
        print(f"Error: {type(e).__name__}: {e}")
        print()
        print("💡 Troubleshooting:")
        print("   1. Make sure PostgreSQL is running")
        print("   2. Check username/password (default: postgres/postgres)")
        print("   3. Verify you have permission to create databases")
        print("   4. Try manually:")
        print("      psql -U postgres")
        print("      DROP DATABASE IF EXISTS scalper_bot;")
        print("      CREATE DATABASE scalper_bot;")
        print()
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    success = asyncio.run(recreate_database())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
