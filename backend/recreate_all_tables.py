#!/usr/bin/env python3
"""
Script to drop and recreate ALL database tables with the correct schema
WARNING: This will delete all existing data!
"""
import asyncio
from sqlalchemy import text
from app.db.session import engine, Base

async def recreate_all_tables():
    """Drop and recreate all tables"""
    print("⚠️  WARNING: This will delete all existing data!")
    print("\nDropping all tables and enum types...")

    async with engine.begin() as conn:
        # Drop all tables
        await conn.execute(text("DROP TABLE IF EXISTS orders CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS activity_logs CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS trades CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS telegram_connections CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS bots CASCADE"))
        print("✅ All tables dropped")

        # Drop all enum types
        await conn.execute(text("DROP TYPE IF EXISTS orderside CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS ordertype CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS orderstatus CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS botstatus CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS exchange CASCADE"))
        print("✅ All enum types dropped")

        # Create all tables with correct schema
        await conn.run_sync(Base.metadata.create_all)
        print("✅ All tables created with correct schema")

    print("\n✅ Database recreated successfully!")
    print("\nYou can now:")
    print("  - Create new bots via the UI")
    print("  - Test the start/stop functionality with live orders")

if __name__ == '__main__':
    asyncio.run(recreate_all_tables())
