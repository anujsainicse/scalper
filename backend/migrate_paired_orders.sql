-- Migration: Add paired_order_id to orders table
-- Date: 2025-10-21
-- Purpose: Enable tracking of buy-sell order pairs for automatic opposite order placement

-- Add paired_order_id column with self-referential foreign key
ALTER TABLE orders
ADD COLUMN IF NOT EXISTS paired_order_id UUID REFERENCES orders(id);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS ix_orders_paired_order_id ON orders(paired_order_id);

-- Verify the change
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'orders' AND column_name = 'paired_order_id';
