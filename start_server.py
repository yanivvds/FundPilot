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

# Load .env at module level so environment variables are available when uvicorn
# imports this module (before __main__ is reached).
load_dotenv(Path(__file__).resolve().parent / ".env")

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
    """Bouw de frontend web component en kopieer naar static/.

    NOTE: This function is intentionally NOT called at startup anymore.
    Building the frontend is the deploy script's responsibility (run it once
    before starting the server, e.g. in CI/CD or a Dockerfile RUN step).
    Call this function manually if you need to rebuild locally.
    """
    # Skip rebuild if the static bundle already exists (e.g. Docker pre-built)
    if STATIC_JS.exists() and os.getenv("SKIP_FRONTEND_BUILD", "").lower() in ("1", "true"):
        print("  [frontend] Bestaande build gevonden, rebuild overgeslagen.")
        return

    if not FRONTEND_DIR.exists():
        print("  [frontend] Map niet gevonden, build overgeslagen.")
        return

    npm_path = shutil.which("npm")
    if not npm_path:
        print("  [frontend] npm niet gevonden, build overgeslagen.")
        return

    print("  [frontend] npm run build...")
    result = subprocess.run(
        [npm_path, "run", "build"],
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


def _print_startup_info():
    """Print startup information about the server configuration."""
    print("FundPilot Multi-Database Chat Server starten...")
    print()
    print("FundPilot Agent succesvol aangemaakt.")
    print(f"  Model:     {os.getenv('OPENAI_MODEL', 'gpt-4o')}")
    print(f"  Server:    {os.getenv('MSSQL_SERVER', 'server')}")
    print(f"  Databases: {len(DATABASES)} -- {', '.join(DATABASES[:3])} + Archive")
    print(f"  Modus:     Alleen-lezen (SELECT)")
    print()
    print("Webserver wordt gestart...")
    print("  Open:     http://localhost:8000")
    print("  API docs: http://localhost:8000/docs")
    print("  Druk Ctrl+C om te stoppen")
    print()


# ---------------------------------------------------------------------------
# Module-level app creation — required for `uvicorn start_server:app`
# ---------------------------------------------------------------------------

try:
    # -- Validate keys: secret keys must NEVER reach the browser --------
    _publishable_key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    if _publishable_key.startswith("sb_secret_") or _publishable_key.startswith("sbp_"):
        raise ValueError(
            "SUPABASE_PUBLISHABLE_KEY contains a secret key! "
            "Use the publishable key (sb_publishable_...) for the browser. "
            "The secret key must only be used server-side (SUPABASE_SECRET_KEY)."
        )

    _require_mfa = os.getenv("REQUIRE_MFA", "true").lower() == "true"

    agent = create_fundpilot_agent()

    server = VannaFastAPIServer(
        agent,
        config={
            "static_folder": str(ROOT / "static"),
            "img_folder": str(ROOT / "img"),
            "cdn_url": "/static/vanna-components.js",
            "supabase_url": os.getenv("SUPABASE_URL", ""),
            "supabase_publishable_key": _publishable_key,
            "require_mfa": _require_mfa,
            "cors": {
                "enabled": True,
                "allow_origins": os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
                "allow_credentials": True,
                "allow_methods": ["GET", "POST"],
                "allow_headers": ["Authorization", "Content-Type"],
            },
        },
    )

    app = server.create_app()

    # Create root directory static files explicit route
    from fastapi.staticfiles import StaticFiles
    import os
    if os.path.exists(str(ROOT / "static")):
        app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="root_static")
    if os.path.exists(str(ROOT / "img")):
        app.mount("/img", StaticFiles(directory=str(ROOT / "img")), name="root_img")

    _print_startup_info()

except Exception as _startup_exc:
    raise RuntimeError(
        f"Server kon niet starten: {_startup_exc}\n\n"
        "Probeer het volgende:\n"
        "1. Controleer je .env bestand\n"
        "2. Controleer of SQL Server bereikbaar is op server\n"
        "3. Controleer je OpenAI API key\n"
        "4. Installeer dependencies:\n"
        "   pip install 'vanna[fastapi,mssql,openai,chromadb]' python-dotenv sqlparse"
    ) from _startup_exc


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    try:
        uvicorn.run("start_server:app", host="127.0.0.1", port=port)
    except KeyboardInterrupt:
        print("\nServer gestopt door gebruiker.")
