#!/bin/bash
# ============================================================================
# FundPilot Setup Script
# ============================================================================
# Installeert dependencies, extraheert database-schema's, en traint de agent.
#
# Gebruik:
#   chmod +x scripts/setup_fundpilot.sh
#   ./scripts/setup_fundpilot.sh              # Volledige setup
#   ./scripts/setup_fundpilot.sh --skip-deps  # Overslaan van pip install
#   ./scripts/setup_fundpilot.sh --retrain    # Wis geheugen en hertrain
# ============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

SKIP_DEPS=false
RETRAIN=false

for arg in "$@"; do
    case $arg in
        --skip-deps) SKIP_DEPS=true ;;
        --retrain)   RETRAIN=true ;;
        *)           echo "Onbekende optie: $arg"; exit 1 ;;
    esac
done

echo "🚀 FundPilot Setup"
echo "============================================================"
echo "Projectmap: $PROJECT_DIR"
echo

# ── 1. Controleer .env ──────────────────────────────────────────────────

if [ ! -f .env ]; then
    echo "❌ .env bestand niet gevonden!"
    echo "   Kopieer .env.example naar .env en vul je gegevens in."
    exit 1
fi

echo "✅ .env gevonden"

# ── 2. Installeer dependencies ──────────────────────────────────────────

if [ "$SKIP_DEPS" = false ]; then
    echo
    echo "📦 Dependencies installeren..."
    pip install -q 'vanna[fastapi,mssql,openai,chromadb]' python-dotenv sqlparse pyodbc
    echo "✅ Dependencies geïnstalleerd"
else
    echo "⏩ Dependencies overgeslagen (--skip-deps)"
fi

# ── 3. Maak mappen aan ──────────────────────────────────────────────────

mkdir -p schema_cache chromadb_data vanna_data docs

# ── 4. Test database-connectiviteit ─────────────────────────────────────

echo
echo "🔌 Database-connectiviteit testen..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

import pyodbc

databases = {
    'CWESystemConfig': os.getenv('MSSQL_CONN_STR_CONFIG'),
    'CWESystemData': os.getenv('MSSQL_CONN_STR_DATA'),
    'CWEProjectData': os.getenv('MSSQL_CONN_STR_PROJECT'),
    'CWESystemConfig_Archive': os.getenv('MSSQL_CONN_STR_CONFIG_ARCHIVE'),
    'CWESystemData_Archive': os.getenv('MSSQL_CONN_STR_DATA_ARCHIVE'),
    'CWEProjectData_Archive': os.getenv('MSSQL_CONN_STR_PROJECT_ARCHIVE'),
}

success = 0
for name, conn_str in databases.items():
    if not conn_str:
        print(f'  ⚠️  {name}: geen connectiestring')
        continue
    try:
        conn_str = conn_str.strip().strip('\"').strip(\"'\")
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES')
        count = cursor.fetchone()[0]
        conn.close()
        print(f'  ✅ {name}: {count} tabellen')
        success += 1
    except Exception as e:
        print(f'  ❌ {name}: {e}')

print(f'\n  Resultaat: {success}/{len(databases)} databases bereikbaar')
if success == 0:
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Geen enkele database bereikbaar. Controleer je .env instellingen."
    exit 1
fi

# ── 5. Extraheer schema's ──────────────────────────────────────────────

echo
echo "📋 Schema's extraheren uit alle databases..."
python scripts/extract_schemas.py

if [ ! -f schema_cache/all_schemas.json ]; then
    echo "❌ Schema-extractie mislukt — all_schemas.json niet aangemaakt."
    exit 1
fi

echo "✅ Schema's geëxtraheerd"

# ── 6. Train de agent ──────────────────────────────────────────────────

echo
if [ "$RETRAIN" = true ]; then
    echo "🎓 Agent hertrainen (geheugen wordt gewist)..."
    python scripts/train_agent.py --clear
else
    echo "🎓 Agent trainen..."
    python scripts/train_agent.py
fi

echo "✅ Training voltooid"

# ── 7. Valideer configuratie ────────────────────────────────────────────

echo
echo "🔍 Configuratie valideren..."
python fundpilot_config.py

# ── 8. Samenvatting ────────────────────────────────────────────────────

echo
echo "============================================================"
echo "✅ FundPilot Setup Voltooid!"
echo "============================================================"
echo
echo "Start de webserver met:"
echo "  python start_server.py"
echo
echo "Of start de CLI chat met:"
echo "  python chat_with_database.py"
echo
echo "Open daarna: http://localhost:8000"
echo "============================================================"
