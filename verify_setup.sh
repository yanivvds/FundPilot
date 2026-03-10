#!/bin/bash

# Quick verification script to check if everything is set up correctly
# Run this after setup.sh to verify your environment

echo "🔍 Verifying Fundpilot Setup..."
echo "==============================="

# Check if virtual environment exists
if [ -d ".venv" ]; then
    echo "✅ Virtual environment found"
else
    echo "❌ Virtual environment missing - run ./setup.sh"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if .env exists
if [ -f ".env" ]; then
    echo "✅ .env file found"
else
    echo "❌ .env file missing - copy from .env.example and configure"
    exit 1
fi

# Check if required Python packages are installed
echo "🐍 Checking Python packages..."
python -c "import vanna, pyodbc, dotenv; print('✅ Required packages installed')" 2>/dev/null || {
    echo "❌ Missing packages - run: pip install -r requirements.txt"
    exit 1
}

# Check ODBC drivers
echo "🔌 Checking ODBC drivers..."
python -c "import pyodbc; drivers = pyodbc.drivers(); assert any('SQL Server' in d for d in drivers), 'No SQL Server driver'; print('✅ ODBC drivers available')" 2>/dev/null || {
    echo "❌ ODBC drivers missing - run: brew install msodbcsql18"
    exit 1
}

# Check environment variables
echo "🔧 Checking environment configuration..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required = ['OPENAI_API_KEY', 'MSSQL_CONN_STR']
missing = [var for var in required if not os.getenv(var) or 'your_' in os.getenv(var, '')]

if missing:
    print(f'❌ Missing/incomplete environment variables: {missing}')
    print('   Please update your .env file')
    exit(1)
else:
    print('✅ Environment variables configured')
"

if [ $? -ne 0 ]; then
    exit 1
fi

echo ""
echo "🎉 Setup Verification Complete!"
echo "=============================="
echo ""
echo "✅ All components are properly installed"
echo "✅ Environment is configured"
echo ""
echo "🚀 Ready to start:"
echo "   ./start.sh"
echo ""
echo "🌐 Then visit: http://localhost:8000"
echo ""