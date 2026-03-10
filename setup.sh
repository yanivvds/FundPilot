#!/bin/bash

echo "🚀 Setting up Fundpilot Database Chat Environment..."
echo "=================================================="

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  This script is designed for macOS. For other systems, follow manual setup in README_SETUP.md"
    exit 1
fi

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew is required but not installed."
    echo "Please install from: https://brew.sh/"
    exit 1
fi

echo "1️⃣ Installing system dependencies..."

# Install unixODBC if not present
if ! brew list unixodbc &> /dev/null; then
    echo "   Installing unixODBC..."
    brew install unixodbc
else
    echo "   ✅ unixODBC already installed"
fi

# Add Microsoft tap if not present
echo "   Adding Microsoft SQL Server ODBC driver..."
if ! brew tap | grep -q "microsoft/mssql-release"; then
    brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
fi

# Install MSSQL ODBC driver if not present
if ! brew list msodbcsql18 &> /dev/null; then
    echo "   Installing Microsoft ODBC Driver 18..."
    brew install msodbcsql18 mssql-tools18
else
    echo "   ✅ Microsoft ODBC Driver 18 already installed"
fi

echo "2️⃣ Setting up Python virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv .venv
else
    echo "   ✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "   Activating virtual environment..."
source .venv/bin/activate

echo "3️⃣ Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "   Verifying Supabase client install..."
python -c "import supabase; print('   ✅ supabase', supabase.__version__)" || {
    echo "   ⚠️  supabase package not found, installing explicitly..."
    pip install "supabase>=2.0.0"
}

echo "4️⃣ Setting up configuration..."

# Create .env from example if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "   ✅ Created .env from .env.example"
        echo "   ⚠️  IMPORTANT: Edit .env with your actual database credentials!"
    else
        echo "   ⚠️  No .env.example found. You'll need to create .env manually."
    fi
else
    echo "   ✅ .env file already exists"
fi

echo "5️⃣ Testing setup..."

# Test if pyodbc can import and see ODBC drivers
echo "   Testing ODBC driver availability..."
python -c "import pyodbc; drivers = pyodbc.drivers(); print(f'Available ODBC drivers: {drivers}'); assert any('SQL Server' in d for d in drivers), 'No SQL Server driver found'"

if [ $? -eq 0 ]; then
    echo "   ✅ ODBC drivers properly installed"
else
    echo "   ❌ ODBC driver test failed"
    exit 1
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database credentials"
echo "2. Add your Supabase URL and Secret key (sb_secret_...) to .env"
echo "3. Enable MFA in Supabase Dashboard → Authentication → MFA"
echo "4. Connect to your VPN if required"
echo "5. Test the setup: python test_connection.py"
echo "6. Start the server: python start_server.py"
echo "7. Visit: http://localhost:8000"
echo ""
echo "💡 To activate the environment later:"
echo "   source .venv/bin/activate"
echo ""