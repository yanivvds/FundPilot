"""
Custom FundPilot tools for multi-database schema inspection.

Provides tools that let the LLM dynamically look up table and column details
from any of the 6 Teleknowledge Connect databases.

All synchronous DB operations are run via asyncio.to_thread() so they do NOT
block the async event loop (which would freeze SSE streaming to the client).
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import List, Optional, Type

import pandas as pd
from pydantic import BaseModel, Field

from vanna.core.tool import Tool, ToolContext, ToolResult
from vanna.components import UiComponent, SimpleTextComponent, DataFrameComponent
from vanna.components.rich.feedback.status_card import StatusCardComponent

logger = logging.getLogger(__name__)

# ── Result limits to prevent LLM context overflow ────────────────────────
MAX_TABLE_MATCHES_PER_DB = 50        # max table-name matches per database
MAX_COLUMN_MATCHES_PER_DB = 100      # max column-name matches per database
MAX_TABLES_FOR_LLM = 200             # max rows when listing all tables in a DB
MAX_SEARCH_RESULTS_FOR_LLM = 80      # max grouped entries sent to LLM


# ── Tool Args Models ─────────────────────────────────────────────────────

class GetSchemaInfoArgs(BaseModel):
    """Arguments for looking up database schema information."""

    database_name: str = Field(
        description=(
            "De naam van de database om te inspecteren. "
            "Keuze uit: CWESystemConfig, CWESystemData, CWEProjectData, "
            "CWESystemConfig_Archive, CWESystemData_Archive, CWEProjectData_Archive"
        )
    )
    table_name: Optional[str] = Field(
        default=None,
        description=(
            "Optioneel: de naam van een specifieke tabel om details van op te halen. "
            "Als niet opgegeven, worden alle tabellen in de database getoond."
        ),
    )


class SearchTablesArgs(BaseModel):
    """Arguments for searching tables across all databases."""

    search_term: str = Field(
        description=(
            "Zoekterm om tabellen te vinden over alle databases. "
            "Zoekt in tabelnamen en kolomnamen. Bijvoorbeeld: 'donor', 'campaign', 'call'."
        )
    )


# ── Allowed databases ────────────────────────────────────────────────────

ALLOWED_DATABASES = {
    "CWESystemConfig",
    "CWESystemData",
    "CWEProjectData",
    "CWESystemConfig_Archive",
    "CWESystemData_Archive",
    "CWEProjectData_Archive",
}


# ── Helper: get pyodbc connection to a specific database ─────────────────

def _get_connection(database_name: str):
    """Create a pyodbc connection to the specified database.

    Re-uses the proven MSSQL_CONN_STR from .env (which already handles the
    password with special characters correctly) and swaps the Database= part.

    NOTE: This is a synchronous function — always call it via asyncio.to_thread().
    """
    import re as _re
    import pyodbc

    base_conn_str = os.getenv("MSSQL_CONN_STR", "")
    if not base_conn_str:
        raise ValueError("MSSQL_CONN_STR environment variable is not set")

    # Swap the Database= segment to target the requested database
    conn_str = _re.sub(
        r"Database=[^;]*",
        f"Database={database_name}",
        base_conn_str,
        count=1,
        flags=_re.IGNORECASE,
    )

    return pyodbc.connect(conn_str, timeout=15)


def _query_schema_tables(database_name: str) -> pd.DataFrame:
    """Synchronous helper: list all tables in a database."""
    conn = _get_connection(database_name)
    try:
        query = """
        SELECT
            t.TABLE_SCHEMA,
            t.TABLE_NAME,
            t.TABLE_TYPE
        FROM INFORMATION_SCHEMA.TABLES t
        WHERE t.TABLE_TYPE IN ('BASE TABLE', 'VIEW')
        ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME
        """
        return pd.read_sql(query, conn)
    finally:
        conn.close()


def _query_schema_columns(database_name: str, table_name: str) -> pd.DataFrame:
    """Synchronous helper: get columns for a specific table."""
    conn = _get_connection(database_name)
    try:
        query = """
        SELECT
            c.COLUMN_NAME,
            c.DATA_TYPE,
            c.CHARACTER_MAXIMUM_LENGTH,
            c.IS_NULLABLE,
            c.COLUMN_DEFAULT,
            CASE WHEN pk.COLUMN_NAME IS NOT NULL THEN 'PK' ELSE '' END AS IS_PK
        FROM INFORMATION_SCHEMA.COLUMNS c
        LEFT JOIN (
            SELECT kcu.COLUMN_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
                ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
            WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
              AND tc.TABLE_NAME = ?
        ) pk ON c.COLUMN_NAME = pk.COLUMN_NAME
        WHERE c.TABLE_NAME = ?
        ORDER BY c.ORDINAL_POSITION
        """
        return pd.read_sql(query, conn, params=[table_name, table_name])
    finally:
        conn.close()


def _search_tables_in_db(database_name: str, search_term: str) -> list[dict]:
    """Synchronous helper: search tables and columns in one database.

    Returns a list of dicts with keys: Database, Tabel, Type, Match.
    Results are capped per category to prevent context overflow.
    """
    results: list[dict] = []
    conn = _get_connection(database_name)
    try:
        # Search in table names (capped)
        table_query = f"""
        SELECT TOP {MAX_TABLE_MATCHES_PER_DB} TABLE_NAME, TABLE_TYPE
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME LIKE ? AND TABLE_TYPE IN ('BASE TABLE', 'VIEW')
        ORDER BY TABLE_NAME
        """
        tables_df = pd.read_sql(table_query, conn, params=[f"%{search_term}%"])
        for _, row in tables_df.iterrows():
            results.append({
                "Database": database_name,
                "Tabel": row["TABLE_NAME"],
                "Type": row["TABLE_TYPE"],
                "Match": "tabelnaam",
            })

        # Search in column names (capped) — grouped by table
        col_query = f"""
        SELECT TOP {MAX_COLUMN_MATCHES_PER_DB}
            c.TABLE_NAME, c.COLUMN_NAME, c.DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS c
        JOIN INFORMATION_SCHEMA.TABLES t
            ON c.TABLE_NAME = t.TABLE_NAME AND c.TABLE_SCHEMA = t.TABLE_SCHEMA
        WHERE c.COLUMN_NAME LIKE ? AND t.TABLE_TYPE IN ('BASE TABLE', 'VIEW')
        ORDER BY c.TABLE_NAME, c.COLUMN_NAME
        """
        cols_df = pd.read_sql(col_query, conn, params=[f"%{search_term}%"])
        for _, row in cols_df.iterrows():
            results.append({
                "Database": database_name,
                "Tabel": row["TABLE_NAME"],
                "Type": f"kolom: {row['COLUMN_NAME']} ({row['DATA_TYPE']})",
                "Match": "kolomnaam",
            })
    finally:
        conn.close()
    return results


def _summarize_search_results(all_results: list[dict]) -> str:
    """Build a compact grouped summary for the LLM.

    Groups by database → table, listing matching columns per table.
    This drastically reduces token count vs. one-row-per-column.
    """
    from collections import defaultdict

    # Separate table-name matches and column-name matches
    table_matches: dict[str, list[str]] = defaultdict(list)  # db → [table, ...]
    col_matches: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))  # db → table → [col_desc]

    for r in all_results:
        db = r["Database"]
        tbl = r["Tabel"]
        if r["Match"] == "tabelnaam":
            table_matches[db].append(tbl)
        elif r["Match"] == "kolomnaam":
            col_matches[db][tbl].append(r["Type"].replace("kolom: ", ""))

    lines: list[str] = []
    entry_count = 0

    # Table-name matches
    for db in sorted(table_matches):
        tables = table_matches[db]
        lines.append(f"\n[{db}] — {len(tables)} tabellen met naam-match:")
        shown = tables[:30]
        for t in shown:
            lines.append(f"  • {t}")
            entry_count += 1
        if len(tables) > 30:
            lines.append(f"  ... en nog {len(tables) - 30} tabellen")

    # Column-name matches — grouped
    for db in sorted(col_matches):
        tables_in_db = col_matches[db]
        total_cols = sum(len(v) for v in tables_in_db.values())
        lines.append(f"\n[{db}] — kolom-matches in {len(tables_in_db)} tabellen ({total_cols} totaal):")
        for tbl in sorted(tables_in_db):
            if entry_count >= MAX_SEARCH_RESULTS_FOR_LLM:
                remaining = len(tables_in_db) - len([t for t in sorted(tables_in_db) if t <= tbl])
                lines.append(f"  ... en nog {remaining + 1} tabellen (afgekapt om context te besparen)")
                break
            cols = tables_in_db[tbl]
            cols_str = ", ".join(cols[:5])
            if len(cols) > 5:
                cols_str += f" (+{len(cols) - 5} meer)"
            lines.append(f"  • {tbl}: {cols_str}")
            entry_count += 1

    return "\n".join(lines)


# ── GetTableSchemaInfoTool ───────────────────────────────────────────────

class GetTableSchemaInfoTool(Tool[GetSchemaInfoArgs]):
    """Tool to inspect database schema (tables and columns) dynamically."""

    @property
    def name(self) -> str:
        return "get_table_schema_info"

    @property
    def description(self) -> str:
        return (
            "Haal schema-informatie op van een database: toon alle tabellen, "
            "of de kolommen en datatypes van een specifieke tabel. "
            "Gebruik dit als je niet zeker weet welke tabellen of kolommen beschikbaar zijn."
        )

    def get_args_schema(self) -> Type[GetSchemaInfoArgs]:
        return GetSchemaInfoArgs

    async def execute(
        self, context: ToolContext, args: GetSchemaInfoArgs
    ) -> ToolResult:
        """Execute schema lookup — DB I/O runs in a background thread."""
        db = args.database_name

        if db not in ALLOWED_DATABASES:
            msg = f"Ongeldige database: '{db}'. Keuze uit: {', '.join(sorted(ALLOWED_DATABASES))}"
            return ToolResult(
                success=False,
                result_for_llm=msg,
                ui_component=UiComponent(
                    rich_component=StatusCardComponent(
                        title="Database niet beschikbaar",
                        status="error",
                        description=msg,
                        icon="❌",
                    ),
                    simple_component=SimpleTextComponent(text=f"❌ {msg}"),
                ),
            )

        try:
            # Guardrail: prevent listing ALL tables in huge project databases
            # (the LLM already has the column structure in its system prompt)
            if not args.table_name and db in ("CWEProjectData", "CWEProjectData_Archive"):
                redirect_msg = (
                    f"⚠️ [{db}] bevat {'119' if db == 'CWEProjectData' else '2311'}+ tabellen. "
                    f"De kolomstructuur staat al in je systeem-prompt (alle tabellen hebben dezelfde kolommen). "
                    f"Om tabelnamen op te halen, gebruik run_sql:\n"
                    f"SELECT TABLE_NAME FROM [{db}].INFORMATION_SCHEMA.TABLES "
                    f"WHERE TABLE_TYPE='BASE TABLE' ORDER BY TABLE_NAME"
                )
                return ToolResult(
                    success=True,
                    result_for_llm=redirect_msg,
                    ui_component=UiComponent(
                        rich_component=StatusCardComponent(
                            title=f"[{db}] — Gebruik SQL voor tabellijst",
                            status="info",
                            description=redirect_msg,
                            icon="💡",
                        ),
                        simple_component=SimpleTextComponent(text=redirect_msg),
                    ),
                )

            if args.table_name:
                df = await asyncio.to_thread(
                    _query_schema_columns, db, args.table_name
                )

                if df.empty:
                    msg = f"Tabel '{args.table_name}' niet gevonden in [{db}]."
                    return ToolResult(
                        success=False,
                        result_for_llm=msg,
                        ui_component=UiComponent(
                            rich_component=StatusCardComponent(
                                title="Tabel niet gevonden",
                                status="warning",
                                description=msg,
                                icon="⚠️",
                            ),
                            simple_component=SimpleTextComponent(text=f"❌ {msg}"),
                        ),
                    )

                result_text = f"Kolommen van [{db}].[dbo].[{args.table_name}]:\n\n"
                result_text += df.to_string(index=False)

                return ToolResult(
                    success=True,
                    result_for_llm=result_text,
                    ui_component=UiComponent(
                        rich_component=DataFrameComponent.from_records(
                            records=df.to_dict("records"),
                            title=f"[{db}].[dbo].[{args.table_name}]",
                            description=f"{len(df)} kolommen",
                        ),
                        simple_component=SimpleTextComponent(text=result_text),
                    ),
                )
            else:
                df = await asyncio.to_thread(_query_schema_tables, db)

                # Build a compact summary for LLM (large DBs have 2000+ tables)
                total = len(df)
                shown_df = df.head(MAX_TABLES_FOR_LLM)
                result_text = f"Tabellen in [{db}] ({total} totaal):\n\n"
                result_text += shown_df.to_string(index=False)
                if total > MAX_TABLES_FOR_LLM:
                    result_text += f"\n\n... en nog {total - MAX_TABLES_FOR_LLM} tabellen (gebruik search_tables_across_databases om specifieke tabellen te vinden)"

                return ToolResult(
                    success=True,
                    result_for_llm=result_text,
                    ui_component=UiComponent(
                        rich_component=DataFrameComponent.from_records(
                            records=df.to_dict("records"),
                            title=f"Tabellen in [{db}]",
                            description=f"{len(df)} tabellen/views",
                        ),
                        simple_component=SimpleTextComponent(text=result_text),
                    ),
                )

        except Exception as e:
            logger.exception("Schema ophalen mislukt voor [%s]", db)
            msg = f"Fout bij ophalen schema van [{db}]: {str(e)}"
            return ToolResult(
                success=False,
                result_for_llm=msg,
                ui_component=UiComponent(
                    rich_component=StatusCardComponent(
                        title="Schema ophalen mislukt",
                        status="error",
                        description=msg,
                        icon="❌",
                    ),
                    simple_component=SimpleTextComponent(text=f"❌ {msg}"),
                ),
                error=str(e),
            )


# ── SearchTablesAcrossDatabasesTool ──────────────────────────────────────

class SearchTablesAcrossDatabasesTool(Tool[SearchTablesArgs]):
    """Tool to search for tables and columns across all 6 databases."""

    @property
    def name(self) -> str:
        return "search_tables_across_databases"

    @property
    def description(self) -> str:
        return (
            "Zoek naar tabellen en kolommen over alle 6 databases heen. "
            "Gebruik dit als je niet weet in welke database een bepaalde tabel staat. "
            "Zoekt op tabelnaam en kolomnaam."
        )

    def get_args_schema(self) -> Type[SearchTablesArgs]:
        return SearchTablesArgs

    async def execute(
        self, context: ToolContext, args: SearchTablesArgs
    ) -> ToolResult:
        """Search across all databases — DB I/O runs in background threads."""
        search = args.search_term
        all_results: list[dict] = []

        for db_name in sorted(ALLOWED_DATABASES):
            try:
                results = await asyncio.to_thread(
                    _search_tables_in_db, db_name, search
                )
                all_results.extend(results)
            except Exception as e:
                logger.warning("Zoeken in [%s] mislukt: %s", db_name, e)
                all_results.append({
                    "Database": db_name,
                    "Tabel": f"FOUT: {str(e)[:80]}",
                    "Type": "error",
                    "Match": "error",
                })

        if not all_results:
            msg = f"Geen tabellen of kolommen gevonden voor zoekterm '{search}'."
            return ToolResult(
                success=True,
                result_for_llm=msg,
                ui_component=UiComponent(
                    rich_component=StatusCardComponent(
                        title="Geen resultaten",
                        status="warning",
                        description=msg,
                        icon="🔍",
                    ),
                    simple_component=SimpleTextComponent(text=msg),
                ),
            )

        df = pd.DataFrame(all_results)

        # Build compact GROUPED summary for LLM (prevents token overflow)
        summary_text = f"Zoekresultaten voor '{search}' ({len(df)} matches over {len(ALLOWED_DATABASES)} databases):\n"
        summary_text += _summarize_search_results(all_results)

        # Full result stays in UI DataFrame only
        ui_text = f"Zoekresultaten: '{search}' — {len(all_results)} resultaten"

        return ToolResult(
            success=True,
            result_for_llm=summary_text,
            ui_component=UiComponent(
                rich_component=DataFrameComponent.from_records(
                    records=all_results,
                    title=f"Zoekresultaten: '{search}'",
                    description=f"{len(all_results)} resultaten over {len(ALLOWED_DATABASES)} databases",
                ),
                simple_component=SimpleTextComponent(text=ui_text),
            ),
        )
