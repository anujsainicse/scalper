-- Migration: Add cancellation_reason to orders table
-- Date: 2025-01-22
-- Purpose: Track why orders are cancelled (system vs manual)

-- Add the column (safe with IF NOT EXISTS)
ALTER TABLE orders
ADD COLUMN IF NOT EXISTS cancellation_reason VARCHAR(50);

-- Verify the column was added
SELECT
    column_name,
    data_type,
    character_maximum_length,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'orders'
AND column_name = 'cancellation_reason';

-- Expected output:
-- column_name         | data_type         | character_maximum_length | is_nullable
-- --------------------+-------------------+-------------------------+-------------
-- cancellation_reason | character varying | 50                      | YES
