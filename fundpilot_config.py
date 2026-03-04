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
    """Simple user resolver for FundPilot database access."""

    async def resolve_user(self, request_context: RequestContext) -> User:
        user_email = (
            request_context.get_cookie("vanna_email") or "fundpilot@example.com"
        )
        group = "admin" if "admin" in user_email else "user"
        return User(
            id=user_email,
            email=user_email,
            group_memberships=[group, "user"],
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