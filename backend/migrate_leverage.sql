-- Migration: Add leverage column and clean old data
-- Run this with: psql -U anujsainicse -d scalper_bot -f migrate_leverage.sql

\echo '=== Scalper Bot Database Migration ==='
\echo ''

-- Check if leverage column exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='bots' AND column_name='leverage'
    ) THEN
        ALTER TABLE bots ADD COLUMN leverage INTEGER DEFAULT 3;
        RAISE NOTICE '✓ Added leverage column with default value 3';
    ELSE
        RAISE NOTICE '✓ Leverage column already exists';
    END IF;
END $$;

\echo ''
\echo '=== Cleaning Old Data ==='

-- Delete all data (in correct order due to foreign keys)
DELETE FROM trades;
\echo '✓ Deleted all trades'

DELETE FROM activity_logs;
\echo '✓ Deleted all activity logs'

DELETE FROM orders;
\echo '✓ Deleted all orders'

DELETE FROM bots;
\echo '✓ Deleted all bots'

\echo ''
\echo '=== Verification ==='

-- Show row counts
SELECT 'bots' as table_name, COUNT(*) as row_count FROM bots
UNION ALL
SELECT 'orders' as table_name, COUNT(*) as row_count FROM orders
UNION ALL
SELECT 'trades' as table_name, COUNT(*) as row_count FROM trades
UNION ALL
SELECT 'activity_logs' as table_name, COUNT(*) as row_count FROM activity_logs;

\echo ''
\echo '=== Summary ==='
\echo '✅ Database is now clean and ready!'
\echo '✅ Leverage column: Added/Verified'
\echo '✅ All data: Deleted'
\echo ''
\echo '🎉 You can now create new bots with leverage field!'
