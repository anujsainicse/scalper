#!/usr/bin/env python3
"""
Script to drop and recreate the orders table with the correct schema
"""
import asyncio
from sqlalchemy import text
from app.db.session import engine
from app.models.order import Order
from app.models.bot import Bot

async def recreate_orders_table():
    """Drop and recreate orders table"""
    print("Dropping existing orders table and enum types...")

    async with engine.begin() as conn:
        # Drop the existing orders table
        await conn.execute(text("DROP TABLE IF EXISTS orders CASCADE"))
        print("✅ Existing orders table dropped")

        # Drop enum types if they exist
        await conn.execute(text("DROP TYPE IF EXISTS orderside CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS ordertype CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS orderstatus CASCADE"))
        print("✅ Existing enum types dropped")

        # Create the orders table with correct schema
        await conn.run_sync(Order.__table__.create)
        print("✅ Orders table created with correct schema")

    print("\n✅ Orders table recreated successfully!")

if __name__ == '__main__':
    asyncio.run(recreate_orders_table())
