#!/bin/bash

# Recreate Database Script
# This will drop and recreate the scalper_bot database with all tables

echo ""
echo "================================================================================"
echo "  DATABASE RECREATION - This will DELETE ALL DATA!"
echo "================================================================================"
echo ""

# Get confirmation
read -p "Are you sure you want to DROP the scalper_bot database? (yes/no): " response

if [ "$response" != "yes" ]; then
    echo "❌ Aborted by user"
    exit 1
fi

echo ""
echo "🔄 Starting database recreation..."
echo ""

# Activate venv and run Python script
if [ -f "venv/bin/activate" ]; then
    echo "📍 Activating virtual environment..."
    source venv/bin/activate
    echo "   ✅ Virtual environment activated"
    echo ""
fi

echo "🚀 Running recreation script..."
python recreate_database.py

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Database recreated with latest schema."
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Start backend: uvicorn app.main:app --reload"
    echo "   2. The database now has all tables including cancellation_reason"
    echo ""
else
    echo ""
    echo "❌ FAILED! See error above."
    echo ""
fi

exit $exit_code
