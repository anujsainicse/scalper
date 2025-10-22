#!/usr/bin/env python3
"""
Force Recreate Database Script - Terminates all connections first

This script will:
1. TERMINATE all connections to scalper_bot database
2. DROP the database
3. CREATE fresh database
4. CREATE all tables with latest schema

IMPORTANT: Stop the backend server first if it's running!

Usage:
    python force_recreate_db.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


async def force_recreate_database():
    """Force drop and recreate the database by terminating connections"""

    print()
    print("=" * 80)
    print("  FORCE DATABASE RECREATION - Terminates all connections!")
    print("=" * 80)
    print()
    print("⚠️  IMPORTANT: Make sure to stop the backend server first!")
    print("   (Press Ctrl+C in the terminal running uvicorn)")
    print()

    response = input("Are you SURE you want to DROP the scalper_bot database? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Aborted by user")
        return False

    print()
    print("🔄 Starting forced database recreation...")
    print()

    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        from app.models.bot import Base
        import os

        db_user = os.getenv("USER", "anujsainicse")
        postgres_url = f"postgresql+asyncpg://{db_user}@localhost:5432/postgres"

        print("📍 Step 1: Connecting to PostgreSQL server...")
        print(f"   Using database user: {db_user}")
        admin_engine = create_async_engine(postgres_url, isolation_level="AUTOCOMMIT")

        async with admin_engine.connect() as conn:
            # Terminate all connections to scalper_bot
            print("🔌 Step 2: Terminating all connections to 'scalper_bot' database...")
            try:
                result = await conn.execute(text("""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = 'scalper_bot'
                    AND pid <> pg_backend_pid();
                """))
                terminated = len(result.fetchall())
                print(f"   ✅ Terminated {terminated} connection(s)")
            except Exception as e:
                print(f"   ⚠️  Warning: {e}")

            # Drop database
            print("🗑️  Step 3: Dropping 'scalper_bot' database...")
            try:
                await conn.execute(text("DROP DATABASE IF EXISTS scalper_bot;"))
                print("   ✅ Database dropped successfully")
            except Exception as e:
                print(f"   ❌ Failed to drop: {e}")
                return False

            # Create database
            print("🏗️  Step 4: Creating new 'scalper_bot' database...")
            await conn.execute(text("CREATE DATABASE scalper_bot;"))
            print("   ✅ Database created successfully")

        await admin_engine.dispose()
        print()

        # Create tables
        print("📍 Step 5: Connecting to new 'scalper_bot' database...")
        app_url = f"postgresql+asyncpg://{db_user}@localhost:5432/scalper_bot"
        app_engine = create_async_engine(app_url)

        print("🏗️  Step 6: Creating all tables with latest schema...")
        async with app_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("   ✅ All tables created")
        print()

        # Verify
        print("✅ Step 7: Verifying setup...")
        async with app_engine.connect() as conn:
            # Check tables
            result = await conn.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"   📋 Tables: {', '.join(tables)}")

            # Check cancellation_reason column
            result = await conn.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'orders' AND column_name = 'cancellation_reason';
            """))
            if result.fetchone():
                print("   ✅ cancellation_reason column EXISTS")
            else:
                print("   ❌ cancellation_reason column NOT FOUND!")

        await app_engine.dispose()

        print()
        print("=" * 80)
        print("  ✅ SUCCESS! Database recreated with latest schema")
        print("=" * 80)
        print()
        print("🚀 Next steps:")
        print("   1. Start backend: uvicorn app.main:app --reload")
        print("   2. All tables include the latest schema with cancellation_reason")
        print()

        return True

    except Exception as e:
        print()
        print("=" * 80)
        print("  ❌ FAILED!")
        print("=" * 80)
        print(f"\nError: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(force_recreate_database())
    sys.exit(0 if success else 1)
