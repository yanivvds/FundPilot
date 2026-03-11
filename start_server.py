"""
FundPilot -- FastAPI server voor multi-database chat met Teleknowledge Connect.
Biedt een webinterface om in natuurlijke taal (Nederlands) te chatten met 6 databases.
"""

import os
import shutil
import subprocess
import logging
from pathlib import Path
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

ROOT = Path(__file__).parent
FRONTEND_DIR = ROOT / "frontends" / "webcomponent"
DIST_JS = FRONTEND_DIR / "dist" / "vanna-components.js"
STATIC_JS = ROOT / "static" / "vanna-components.js"


def build_frontend():
    """Bouw de frontend web component en kopieer naar static/."""
    # Skip rebuild if the static bundle already exists (e.g. Docker pre-built)
    if STATIC_JS.exists() and os.getenv("SKIP_FRONTEND_BUILD", "").lower() in ("1", "true"):
        print("  [frontend] Bestaande build gevonden, rebuild overgeslagen.")
        return

    if not FRONTEND_DIR.exists():
        print("  [frontend] Map niet gevonden, build overgeslagen.")
        return

    if not shutil.which("npm"):
        print("  [frontend] npm niet gevonden, build overgeslagen.")
        return

    print("  [frontend] npm run build...")
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("  [frontend] Build mislukt:")
        print(result.stdout[-2000:] if result.stdout else "")
        print(result.stderr[-2000:] if result.stderr else "")
        return

    if DIST_JS.exists():
        STATIC_JS.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(DIST_JS, STATIC_JS)
        print(f"  [frontend] Gebouwd en gekopieerd naar {STATIC_JS.relative_to(ROOT)}")
    else:
        print("  [frontend] dist/vanna-components.js niet gevonden na build.")


def main():
    """Start de FundPilot webserver."""
    print("FundPilot Multi-Database Chat Server starten...")
    print()

    try:
        load_dotenv()

        # Build frontend before starting the server
        build_frontend()
        print()

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
