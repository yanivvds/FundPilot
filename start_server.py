"""
FundPilot -- FastAPI server voor multi-database chat met Teleknowledge Connect.
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
    print("FundPilot Multi-Database Chat Server starten...")
    print()

    try:
        load_dotenv()
        agent = create_fundpilot_agent()

        print("FundPilot Agent succesvol aangemaakt.")
        print(f"  Model:     {os.getenv('OPENAI_MODEL', 'gpt-4o')}")
        print(f"  Server:    {os.getenv('MSSQL_SERVER', '192.168.78.123')}")
        print(f"  Databases: {len(DATABASES)} -- {', '.join(DATABASES[:3])} + Archive")
        print(f"  Modus:     Alleen-lezen (SELECT)")
        print()

        # -- Validate keys: secret keys must NEVER reach the browser --------
        publishable_key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
        if publishable_key.startswith("sb_secret_") or publishable_key.startswith("sbp_"):
            raise ValueError(
                "SUPABASE_PUBLISHABLE_KEY contains a secret key! "
                "Use the publishable key (sb_publishable_...) for the browser. "
                "The secret key must only be used server-side (SUPABASE_SECRET_KEY)."
            )

        require_mfa = os.getenv("REQUIRE_MFA", "true").lower() == "true"

        server = VannaFastAPIServer(
            agent,
            config={
                "cdn_url": "/static/vanna-components.js",
                "supabase_url": os.getenv("SUPABASE_URL", ""),
                "supabase_publishable_key": publishable_key,
                "require_mfa": require_mfa,
                "cors": {
                    "enabled": True,
                    "allow_origins": os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
                    "allow_credentials": True,
                    "allow_methods": ["GET", "POST"],
                    "allow_headers": ["Authorization", "Content-Type"],
                },
            },
        )

        print("Webserver wordt gestart...")
        print("  Open:     http://localhost:8000")
        print("  API docs: http://localhost:8000/docs")
        print("  Druk Ctrl+C om te stoppen")
        print()

        server.run()

    except KeyboardInterrupt:
        print("\nServer gestopt door gebruiker.")
    except Exception as e:
        print(f"Server kon niet starten: {e}")
        print()
        print("Probeer het volgende:")
        print("1. Controleer je .env bestand")
        print("2. Controleer of SQL Server bereikbaar is op 192.168.78.123")
        print("3. Controleer je OpenAI API key")
        print("4. Installeer dependencies:")
        print("   pip install 'vanna[fastapi,mssql,openai,chromadb]' python-dotenv sqlparse")


if __name__ == "__main__":
    main()
