# Database Migration Setup - Alembic

## Overview
This document describes the Alembic database migration setup for the Scalper Bot backend.

## Date: 2025-10-19

## Migration System Setup

### Problem
The application was using `Base.metadata.create_all()` for automatic table creation, which doesn't provide:
- Version control for schema changes
- Rollback capabilities
- Migration history tracking
- Team collaboration on schema changes

### Solution
Implemented Alembic for professional database migration management with async SQLAlchemy support.

## Implementation Details

### 1. Models Package Setup
**File**: `backend/app/models/__init__.py`

Created a central import file to register all models with SQLAlchemy's Base.metadata:

```python
from app.models.bot import Bot, ActivityLog, Trade, TelegramConnection, BotStatus, OrderSide, Exchange
from app.models.credentials import ExchangeCredentials
from app.models.order import Order, OrderStatus, OrderType

__all__ = [
    'Bot', 'ActivityLog', 'Trade', 'TelegramConnection',
    'BotStatus', 'OrderSide', 'Exchange',
    'ExchangeCredentials', 'Order', 'OrderStatus', 'OrderType',
]
```

**Why**: Alembic's autogenerate feature needs all models imported to detect them for migrations.

### 2. Alembic Initialization
**Command**: `alembic init alembic`

**Structure Created**:
```
backend/
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── script.py.mako
│   └── README
├── alembic.ini
```

### 3. Alembic Configuration
**File**: `backend/alembic.ini`

- Commented out default `sqlalchemy.url` setting
- Database URL is loaded dynamically from settings in env.py

### 4. Async SQLAlchemy Support
**File**: `backend/alembic/env.py`

**Key Changes**:
```python
import asyncio
from sqlalchemy.ext.asyncio import async_engine_from_config
from app.db.session import Base
from app.core.config import settings
import app.models  # Register all models

# Load database URL from settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
target_metadata = Base.metadata

async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())
```

**Why**: Default Alembic templates don't support async SQLAlchemy. This configuration enables async database operations during migrations.

### 5. Initial Migration
**Command**: `alembic revision --autogenerate -m "add_exchange_credentials_and_orders_tables"`

**Migration File**: `backend/alembic/versions/fef8185d3887_add_exchange_credentials_and_orders_.py`

**Note**: The migration file is empty (contains only `pass` statements) because:
- Tables already existed in the database (created via `Base.metadata.create_all()`)
- Alembic's autogenerate detected no differences between database and models
- This is expected behavior when setting up Alembic on an existing database

### 6. Database Stamping
**Command**: `alembic stamp head`

**Output**:
```
INFO  [alembic.runtime.migration] Running stamp_revision  -> fef8185d3887
```

**Purpose**: Marks the database as being at the current migration version without applying any migrations. This is the correct approach when:
- Setting up Alembic on an existing database
- All tables already exist
- You want to start tracking future changes from this point

### 7. Application Update
**File**: `backend/app/main.py`

**Before**:
```python
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
print("✅ Database tables created")
```

**After**:
```python
# Database tables are managed by Alembic migrations
# To apply migrations, run: alembic upgrade head
# To create new migrations, run: alembic revision --autogenerate -m "description"
# async with engine.begin() as conn:
#     await conn.run_sync(Base.metadata.create_all)

print("✅ Database ready (migrations managed by Alembic)")
```

**Why**: Application startup no longer auto-creates tables. Migrations must be run separately using Alembic commands.

## Common Alembic Commands

### Working Directory
All Alembic commands must be run from the `backend/` directory:
```bash
cd /Users/anujsainicse/claude/scalper/backend
source venv/bin/activate
```

### View Migration History
```bash
alembic history
```

### Check Current Migration Version
```bash
alembic current
```

### Create New Migration
```bash
# Auto-generate migration based on model changes
alembic revision --autogenerate -m "description_of_changes"

# Create empty migration file (for manual changes)
alembic revision -m "description_of_changes"
```

### Apply Migrations
```bash
# Upgrade to latest migration
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Upgrade by one version
alembic upgrade +1
```

### Rollback Migrations
```bash
# Downgrade by one version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>

# Downgrade to base (empty database)
alembic downgrade base
```

### Stamp Database
```bash
# Mark database as being at specific revision
alembic stamp <revision_id>

# Mark as being at latest revision
alembic stamp head
```

## Workflow for Schema Changes

### 1. Modify Models
Edit model files in `backend/app/models/`:
```python
# Example: Add new column to ExchangeCredentials
class ExchangeCredentials(Base):
    __tablename__ = "exchange_credentials"
    # ... existing columns ...
    new_field: Mapped[str] = mapped_column(String, nullable=True)  # New field
```

### 2. Generate Migration
```bash
alembic revision --autogenerate -m "add_new_field_to_exchange_credentials"
```

### 3. Review Migration File
Check the generated migration in `backend/alembic/versions/`:
```python
def upgrade() -> None:
    op.add_column('exchange_credentials',
                  sa.Column('new_field', sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column('exchange_credentials', 'new_field')
```

### 4. Apply Migration
```bash
alembic upgrade head
```

### 5. Verify Changes
```bash
# Check current version
alembic current

# Or connect to database and verify schema
psql postgresql://postgres:postgres@localhost:5432/scalper_bot
\d exchange_credentials
```

## Troubleshooting

### Error: Can't locate revision identified by 'xxx'
**Cause**: Database has old `alembic_version` table referencing non-existent migration.

**Solution**:
```bash
source venv/bin/activate && python -c "
import asyncio
from app.db.session import engine
from sqlalchemy import text

async def drop_alembic_version():
    async with engine.begin() as conn:
        await conn.execute(text('DROP TABLE IF EXISTS alembic_version'))
        print('Dropped alembic_version table')

asyncio.run(drop_alembic_version())
"
```

Then regenerate migration and stamp database.

### Error: Target database is not up to date
**Cause**: Database version doesn't match migration head.

**Solution**:
```bash
# Check current version
alembic current

# Check what migrations exist
alembic history

# Upgrade to latest
alembic upgrade head
```

### Autogenerate Not Detecting Changes
**Cause**: Models not imported in `app/models/__init__.py` or env.py.

**Solution**:
1. Ensure all models are imported in `backend/app/models/__init__.py`
2. Verify `env.py` imports `app.models`
3. Restart Python environment and regenerate migration

## Database Tables

### Current Schema (as of fef8185d3887)
- `alembic_version` - Migration version tracking
- `bots` - Trading bot configurations
- `activity_logs` - Bot activity history
- `trades` - Executed trades
- `telegram_connections` - User-Telegram linkage
- `exchange_credentials` - API credentials for exchanges
- `orders` - Order history and status

## Best Practices

1. **Always Review Auto-generated Migrations**: Alembic's autogenerate is smart but not perfect. Review and edit migration files before applying.

2. **Test Migrations Locally First**: Always test migrations on a development database before production.

3. **Never Edit Applied Migrations**: Once a migration is applied and committed, create a new migration for changes.

4. **Write Reversible Migrations**: Ensure `downgrade()` properly reverses `upgrade()` operations.

5. **Use Descriptive Migration Names**: Use clear, descriptive names that explain what the migration does.

6. **Keep Migrations Small**: Create separate migrations for logically distinct changes.

7. **Backup Before Major Migrations**: Always backup production database before applying migrations.

## Production Deployment

### Initial Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Apply migrations
alembic upgrade head

# 3. Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Updating Existing Deployment
```bash
# 1. Stop application
sudo systemctl stop scalper-bot

# 2. Backup database
pg_dump scalper_bot > backup_$(date +%Y%m%d_%H%M%S).sql

# 3. Pull latest code
git pull

# 4. Apply migrations
source venv/bin/activate
alembic upgrade head

# 5. Restart application
sudo systemctl start scalper-bot
```

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Autogenerate](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
