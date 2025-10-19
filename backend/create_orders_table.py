#!/usr/bin/env python3
"""
Script to create the orders table in the database
Run this if the orders table doesn't exist
"""
import asyncio
from app.db.session import engine, Base
from app.models.order import Order
from app.models.bot import Bot

async def create_tables():
    """Create all tables defined in the models"""
    print("Creating orders table...")

    async with engine.begin() as conn:
        # Create all tables (only creates if they don't exist)
        await conn.run_sync(Base.metadata.create_all)

    print("✅ Orders table created successfully!")

if __name__ == '__main__':
    asyncio.run(create_tables())
