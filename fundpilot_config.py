"""
FundPilot — Multi-database AI agent for Teleknowledge Connect.

Configures a Vanna AI agent that queries across 6 SQL Server databases:
  - CWESystemConfig / CWESystemData / CWEProjectData  (primary)
  - CWESystemConfig_Archive / CWESystemData_Archive / CWEProjectData_Archive

Uses ChromaDB for persistent memory, a read-only SQL runner for safety,
and a custom Dutch system prompt with full database catalog.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from vanna import Agent
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.integrations.openai import OpenAILlmService
from vanna.integrations.mssql import MSSQLRunner
from vanna.integrations.local import LocalFileSystem
from vanna.tools import (
    RunSqlTool,
    VisualizeDataTool,
)
from vanna.tools.agent_memory import (
    SaveQuestionToolArgsTool,
    SearchSavedCorrectToolUsesTool,
    SaveTextMemoryTool,
)

# FundPilot-specific modules
from fundpilot_prompt import FundPilotSystemPromptBuilder
from fundpilot_sql_runner import ReadOnlySqlRunner
from fundpilot_tools import GetTableSchemaInfoTool, SearchTablesAcrossDatabasesTool

logger = logging.getLogger(__name__)


# ── User resolver ────────────────────────────────────────────────────────

class FundpilotUserResolver(UserResolver):
    """Supabase-backed user resolver for FundPilot.

    Requires SUPABASE_URL and SUPABASE_SECRET_KEY to be configured.
    Validates JWTs server-side via Supabase and enforces MFA (AAL2)
    when REQUIRE_MFA=true. If Supabase is not configured, all access
    is denied — there is no guest/anonymous fallback.
    """

    def __init__(self) -> None:
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_SECRET_KEY", "")

        if supabase_url and supabase_key:
            import supabase as _supabase
            self._supabase = _supabase.create_client(
                supabase_url=supabase_url,
                supabase_key=supabase_key,
            )
            self._require_mfa = os.getenv("REQUIRE_MFA", "true").lower() == "true"
            logger.info("FundpilotUserResolver: Supabase auth enabled (MFA=%s)", self._require_mfa)
        else:
            self._supabase = None
            self._require_mfa = False
            logger.error(
                "FundpilotUserResolver: SUPABASE_URL/SUPABASE_SECRET_KEY not set — "
                "ALL access will be denied. Configure these in .env to enable auth."
            )

    async def resolve_user(self, request_context: RequestContext) -> User:
        # ── No Supabase configured → deny all access ───────────────────────
        if self._supabase is None:
            raise PermissionError(
                "Authentication is not configured. Contact your administrator."
            )

        # ── Supabase JWT auth ────────────────────────────────────────────────
        auth_header = request_context.get_header("Authorization") or ""
        if not auth_header.startswith("Bearer "):
            raise PermissionError("Missing or invalid Authorization header")

        token = auth_header.removeprefix("Bearer ").strip()
        if not token:
            raise PermissionError("Missing or invalid Authorization header")

        # Validate the JWT server-side via Supabase
        try:
            response = self._supabase.auth.get_user(token)
        except Exception as exc:
            logger.warning("Supabase token validation failed: %s", exc)
            raise PermissionError("Authentication failed") from None

        supa_user = response.user
        if supa_user is None:
            raise PermissionError("Authentication failed")

        # Enforce MFA (AAL2) when required
        # Token was already validated server-side; we read the aal claim safely.
        if self._require_mfa:
            import base64
            import json as _json

            try:
                parts = token.split(".")
                if len(parts) != 3:
                    raise ValueError("Malformed JWT")
                payload_b64 = parts[1]
                payload_b64 += "=" * (-len(payload_b64) % 4)
                payload = _json.loads(base64.urlsafe_b64decode(payload_b64))
                aal = payload.get("aal")
            except Exception:
                aal = None

            if aal != "aal2":
                raise PermissionError(
                    "MFA verification required. Complete 2FA before accessing FundPilot."
                )

        # Derive Vanna groups from Supabase app_metadata
        app_metadata = supa_user.app_metadata or {}
        roles: list[str] = app_metadata.get("roles", [])

        groups = list(roles) if roles else []
        if "user" not in groups:
            groups.append("user")

        return User(
            id=supa_user.id,
            username=(supa_user.user_metadata or {}).get(
                "name", supa_user.email.split("@")[0] if supa_user.email else supa_user.id
            ),
            email=supa_user.email or "",
            group_memberships=groups,
            metadata={"app_metadata": app_metadata},
        )


# ── Agent memory setup ──────────────────────────────────────────────────

def _create_agent_memory():
    """Create ChromaDB-based persistent agent memory (with fallback to in-memory)."""
    persist_dir = os.getenv("CHROMADB_PERSIST_DIR", "./chromadb_data")

    try:
        from vanna.integrations.chromadb import ChromaAgentMemory

        memory = ChromaAgentMemory(
            persist_directory=persist_dir,
            collection_name="fundpilot_memory",
        )
        logger.info("ChromaDB geheugen geladen uit %s", persist_dir)
        return memory
    except ImportError:
        logger.warning(
            "chromadb niet geïnstalleerd — terugvallen op in-memory geheugen. "
            "Installeer met: pip install chromadb"
        )
        from vanna.integrations.local.agent_memory import DemoAgentMemory

        return DemoAgentMemory(max_items=5000)
    except Exception as e:
        logger.warning(
            "ChromaDB kon niet worden geladen (%s) — terugvallen op in-memory geheugen.",
            e,
        )
        from vanna.integrations.local.agent_memory import DemoAgentMemory

        return DemoAgentMemory(max_items=5000)


# ── Main agent factory ──────────────────────────────────────────────────

def create_fundpilot_agent() -> Agent:
    """Create a FundPilot agent configured for multi-database Teleknowledge Connect querying.

    The agent:
    - Connects to SQL Server via a single ODBC connection (cross-DB queries via three-part naming)
    - Enforces read-only access (SELECT only)
    - Uses ChromaDB for persistent schema & query pattern memory
    - Responds in Dutch with automatic database routing
    """
    # Load environment variables
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        print(
            "⚠️  python-dotenv niet gevonden. Zorg dat omgevingsvariabelen handmatig zijn ingesteld."
        )

    # Validate required environment variables
    required_vars = {
        "OPENAI_API_KEY": "OpenAI API key",
        "MSSQL_CONN_STR": "MS SQL ODBC connectiestring",
    }
    missing = [
        f"{k} ({v})" for k, v in required_vars.items() if not os.getenv(k)
    ]
    if missing:
        raise ValueError(
            f"Ontbrekende omgevingsvariabelen: {', '.join(missing)}\n"
            "Controleer je .env bestand."
        )

    # ── LLM ──────────────────────────────────────────────────────────
    llm = OpenAILlmService(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    # ── SQL runner (read-only wrapper) ───────────────────────────────
    inner_runner = MSSQLRunner(odbc_conn_str=os.getenv("MSSQL_CONN_STR"))
    sql_runner = ReadOnlySqlRunner(inner=inner_runner, max_rows=10000)

    # ── File system ──────────────────────────────────────────────────
    file_system = LocalFileSystem("./vanna_data")

    # ── Agent memory (ChromaDB with fallback) ────────────────────────
    agent_memory = _create_agent_memory()

    # ── System prompt builder ────────────────────────────────────────
    system_prompt_builder = FundPilotSystemPromptBuilder()

    # ── User resolver ────────────────────────────────────────────────
    user_resolver = FundpilotUserResolver()

    # ── Tool registry ────────────────────────────────────────────────
    tools = ToolRegistry()

    # Core SQL tool (read-only, uses three-part naming for cross-DB queries)
    db_tool = RunSqlTool(
        sql_runner=sql_runner,
        file_system=file_system,
        custom_tool_description=(
            "Voer een SQL SELECT-query uit op de Teleknowledge Connect databases. "
            "Gebruik ALTIJD three-part naming: [DatabaseNaam].[dbo].[TabelNaam]. "
            "Beschikbare databases: CWESystemConfig, CWESystemData, CWEProjectData, "
            "CWESystemConfig_Archive, CWESystemData_Archive, CWEProjectData_Archive. "
            "Alleen SELECT-query's zijn toegestaan."
        ),
    )
    tools.register_local_tool(db_tool, access_groups=["admin", "user"])

    # Visualization tool
    tools.register_local_tool(
        VisualizeDataTool(file_system=file_system),
        access_groups=["admin", "user"],
    )

    # Schema inspection tools (for dynamic schema lookup)
    tools.register_local_tool(
        GetTableSchemaInfoTool(),
        access_groups=["admin", "user"],
    )
    tools.register_local_tool(
        SearchTablesAcrossDatabasesTool(),
        access_groups=["admin", "user"],
    )

    # Memory tools (for learning from interactions)
    tools.register_local_tool(
        SaveQuestionToolArgsTool(), access_groups=["admin"]
    )
    tools.register_local_tool(
        SearchSavedCorrectToolUsesTool(), access_groups=["admin", "user"]
    )
    tools.register_local_tool(
        SaveTextMemoryTool(), access_groups=["admin", "user"]
    )

    # ── Agent config ──────────────────────────────────────────────────
    from vanna.core.agent.config import AgentConfig

    agent_config = AgentConfig(
        max_tool_iterations=25,     # multi-DB queries need many tool calls
        stream_responses=True,
        auto_save_conversations=True,
    )

    # ── Create agent ─────────────────────────────────────────────────
    agent = Agent(
        llm_service=llm,
        tool_registry=tools,
        user_resolver=user_resolver,
        agent_memory=agent_memory,
        system_prompt_builder=system_prompt_builder,
        config=agent_config,
    )

    logger.info(
        "FundPilot agent aangemaakt — %d tools geregistreerd, geheugen: %s",
        len(tools._tools) if hasattr(tools, "_tools") else 0,
        type(agent_memory).__name__,
    )

    return agent


def get_db_tool() -> RunSqlTool:
    """Get just the database tool for standalone use (with read-only enforcement)."""
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except ImportError:
        pass

    inner_runner = MSSQLRunner(odbc_conn_str=os.getenv("MSSQL_CONN_STR"))
    sql_runner = ReadOnlySqlRunner(inner=inner_runner, max_rows=10000)
    file_system = LocalFileSystem("./vanna_data")

    return RunSqlTool(sql_runner=sql_runner, file_system=file_system)


if __name__ == "__main__":
    """Quick validation of the FundPilot agent configuration."""
    try:
        agent = create_fundpilot_agent()
        print("✅ FundPilot Multi-Database Agent succesvol aangemaakt!")
        print(f"   Model: {os.getenv('OPENAI_MODEL', 'gpt-4o')}")
        print(f"   Server: {os.getenv('MSSQL_SERVER', '192.168.78.123')}")
        print(f"   Databases: CWESystemConfig, CWESystemData, CWEProjectData + Archive")
        print(f"   Geheugen: {type(agent._agent_memory).__name__ if hasattr(agent, '_agent_memory') else 'onbekend'}")
        print(f"   Modus: Alleen-lezen (SELECT)")
    except Exception as e:
        print(f"❌ Fout bij aanmaken agent: {e}")
        print("\nControleer je .env configuratiebestand.")