# Database Migration - Add Cancellation Reason

## Migration Required

This update adds a `cancellation_reason` column to the `orders` table to distinguish between system-initiated and manual order cancellations.

## How to Run Migration

### Option 1: Using psql (PostgreSQL CLI)

```bash
# Connect to your database and run:
psql scalper_bot -c "ALTER TABLE orders ADD COLUMN IF NOT EXISTS cancellation_reason VARCHAR(50);"
```

### Option 2: Using any PostgreSQL client

Connect to the `scalper_bot` database and execute:

```sql
ALTER TABLE orders ADD COLUMN IF NOT EXISTS cancellation_reason VARCHAR(50);
```

### Option 3: Using Python script

Create a file `run_migration.py`:

```python
import asyncio
from app.db.session import AsyncSessionLocal
from sqlalchemy import text

async def run_migration():
    async with AsyncSessionLocal() as db:
        await db.execute(text(
            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS cancellation_reason VARCHAR(50);"
        ))
        await db.commit()
        print("✅ Migration completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_migration())
```

Then run:
```bash
source venv/bin/activate
python run_migration.py
```

### Option 4: Using Alembic (if configured)

```bash
source venv/bin/activate
alembic upgrade head
```

## Verification

After running the migration, verify it worked:

```sql
-- Check if column exists
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'orders' AND column_name = 'cancellation_reason';
```

Expected output:
```
 column_name        | data_type
--------------------+------------------
 cancellation_reason| character varying
```

## What This Fix Does

**Problem**: Bot updates were triggering auto-stop because:
1. Update process cancels old order
2. WebSocket detects cancellation
3. Auto-stop is triggered (unintended for updates)

**Solution**: Track why orders are cancelled:
- `"UPDATE"` - Bot config updated (don't auto-stop)
- `"STOP"` - Bot stopped by user (don't auto-stop)
- `"DELETE"` - Bot deleted (don't auto-stop)
- `NULL` or other - Manual cancellation (DO auto-stop)

## Files Modified

1. `app/models/order.py` - Added cancellation_reason field
2. `app/schemas/order.py` - Added field to response schema
3. `app/api/v1/endpoints/bots.py` - Set reason in update/stop/delete (3 locations)
4. `app/api/v1/endpoints/websocket.py` - Check reason before auto-stop
5. `alembic/versions/20250122_add_cancellation_reason_to_orders.py` - Migration file

## Testing After Migration

1. **Test Bot Update**:
   - Update a bot's prices
   - Verify bot stays ACTIVE
   - Check order shows `cancellation_reason = "UPDATE"`

2. **Test Manual Cancellation**:
   - Cancel order on exchange manually
   - Verify bot auto-stops
   - Check `cancellation_reason` is NULL

3. **Test Bot Stop**:
   - Stop bot from UI
   - Verify order shows `cancellation_reason = "STOP"`

4. **Test Bot Delete**:
   - Delete bot
   - Verify order shows `cancellation_reason = "DELETE"`

## Rollback (if needed)

If something goes wrong:

```sql
ALTER TABLE orders DROP COLUMN IF EXISTS cancellation_reason;
```

Then revert the code changes via git.

---

**Status**: Migration pending - please run manually before starting the backend server.
