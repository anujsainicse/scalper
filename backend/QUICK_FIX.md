# Quick Fix for Toast Error

## Problem

The backend is trying to set `cancellation_reason` on orders, but the database column doesn't exist yet because the migration hasn't been run.

## Solution - Run This NOW

### Option 1: Direct SQL (Fastest - 10 seconds)

If you have PostgreSQL Postico, TablePlus, pgAdmin, or any PostgreSQL GUI:

1. Connect to `scalper_bot` database
2. Open SQL query window
3. Run this:

```sql
ALTER TABLE orders ADD COLUMN IF NOT EXISTS cancellation_reason VARCHAR(50);
```

4. Restart backend server

### Option 2: Command Line (If psql is available)

```bash
# Find your PostgreSQL installation
which psql

# If found, run:
psql scalper_bot -c "ALTER TABLE orders ADD COLUMN IF NOT EXISTS cancellation_reason VARCHAR(50);"

# Restart backend
```

### Option 3: Python Script (With venv)

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate  # On Windows

# Run migration
python run_migration.py

# Restart backend
```

### Option 4: Quick Python One-Liner

```bash
cd backend
source venv/bin/activate

python -c "
import asyncio
from sqlalchemy import create_engine, text
from app.core.config import settings

# Use sync engine for quick migration
engine = create_engine(settings.DATABASE_URL.replace('+asyncpg', ''))
with engine.connect() as conn:
    conn.execute(text('ALTER TABLE orders ADD COLUMN IF NOT EXISTS cancellation_reason VARCHAR(50);'))
    conn.commit()
    print('✅ Migration done!')
"
```

## Verification

After running the migration, verify it worked:

```sql
-- Check column exists
SELECT column_name FROM information_schema.columns
WHERE table_name = 'orders' AND column_name = 'cancellation_reason';
```

Should return:
```
 column_name
--------------------
 cancellation_reason
```

## After Migration

1. **Restart the backend server**
2. **Try updating a bot** - should work without errors
3. **Check logs** - should see "System-initiated cancellation" messages

## Still Getting Errors?

If you're still seeing toast errors after running the migration:

1. **Check backend logs** for the actual error
2. **Check browser console** for frontend errors
3. Share the error message - it will help me fix it quickly

Common issues:
- Backend not restarted after migration
- Frontend not refreshed (Ctrl+Shift+R to hard refresh)
- Database connection issue
- Different database being used

## Rollback (if needed)

If something goes wrong:

```sql
ALTER TABLE orders DROP COLUMN IF EXISTS cancellation_reason;
```

Then:
```bash
git revert HEAD  # Revert the last commit
```

---

**TL;DR**: Run this SQL and restart backend:
```sql
ALTER TABLE orders ADD COLUMN IF NOT EXISTS cancellation_reason VARCHAR(50);
```
