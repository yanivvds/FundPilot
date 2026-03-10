"""
FundPilot — FastAPI server voor multi-database chat met Teleknowledge Connect.
Biedt een webinterface om in natuurlijke taal (Nederlands) te chatten met 6 databases.
"""

import os
import logging
from dotenv import load_dotenv
from fundpilot_config import create_fundpilot_agent
from vanna.servers.fastapi import VannaFastAPIServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

DATABASES = [
    "CWESystemConfig", "CWESystemData", "CWEProjectData",
    "CWESystemConfig_Archive", "CWESystemData_Archive", "CWEProjectData_Archive",
]


def main():
    """Start de FundPilot webserver."""
    print("🚀 FundPilot Multi-Database Chat Server starten...")
    print()

    try:
        load_dotenv()
        agent = create_fundpilot_agent()

        print("✅ FundPilot Agent succesvol aangemaakt!")
        print(f"🤖 Model: {os.getenv('OPENAI_MODEL', 'gpt-4o')}")
        print(f"🗄️  Server: {os.getenv('MSSQL_SERVER', '192.168.78.123')}")
        print(f"📂 Databases: {len(DATABASES)} — {', '.join(DATABASES[:3])} + Archive")
        print(f"🔒 Modus: Alleen-lezen (SELECT)")
        print()

        server = VannaFastAPIServer(agent)

        print("🌐 Webserver wordt gestart...")
        print("📱 Open: http://localhost:8000")
        print("🔧 API docs: http://localhost:8000/docs")
        print("🛑 Druk Ctrl+C om te stoppen")
        print()

        server.run()

    except KeyboardInterrupt:
        print("\n👋 Server gestopt door gebruiker")
    except Exception as e:
        print(f"❌ Server kon niet starten: {e}")
        print()
        print("🔧 Probeer het volgende:")
        print("1. Controleer je .env bestand")
        print("2. Controleer of SQL Server bereikbaar is op 192.168.78.123")
        print("3. Controleer je OpenAI API key")
        print("4. Installeer dependencies:")
        print("   pip install 'vanna[fastapi,mssql,openai,chromadb]' python-dotenv sqlparse")


if __name__ == "__main__":
    main()