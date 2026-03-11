"""
Custom FundPilot tools for multi-database schema inspection.

Provides tools that let the LLM dynamically look up table and column details
from any of the 6 Teleknowledge Connect databases.

All synchronous DB operations are run via asyncio.to_thread() so they do not
block the async event loop.
"""

from __future__ import annotations

import asyncio
import logging
import os
from collections import defaultdict
from typing import Optional, Type

import pandas as pd
from pydantic import BaseModel, Field

from vanna.core.tool import Tool, ToolContext, ToolResult
from vanna.components import UiComponent, SimpleTextComponent, DataFrameComponent
from vanna.components.rich.feedback.status_card import StatusCardComponent

logger = logging.getLogger(__name__)

MAX_TABLE_MATCHES_PER_DB = 50
MAX_COLUMN_MATCHES_PER_DB = 100
MAX_TABLES_FOR_LLM = 200
MAX_SEARCH_RESULTS_FOR_LLM = 80

ALLOWED_DATABASES = {
    "CWESystemConfig",
    "CWESystemData",
    "CWEProjectData",
    "CWESystemConfig_Archive",
    "CWESystemData_Archive",
    "CWEProjectData_Archive",
}


class GetSchemaInfoArgs(BaseModel):
    """Arguments for looking up database schema information."""

    database_name: str = Field(
        description=(
            "Naam van de database om te inspecteren. "
            "Keuze uit: CWESystemConfig, CWESystemData, CWEProjectData, "
            "CWESystemConfig_Archive, CWESystemData_Archive, CWEProjectData_Archive."
        )
    )
    table_name: Optional[str] = Field(
        default=None,
        description=(
            "Optioneel: specifieke tabelnaam. "
            "Als opgegeven, toon kolommen en datatypes van die tabel. "
            "Als niet opgegeven, toon de tabellen in de database."
        ),
    )


class SearchTablesArgs(BaseModel):
    """Arguments for searching tables across all databases."""

    search_term: str = Field(
        description=(
            "Zoekterm om tabellen of kolommen te vinden over alle databases. "
            "Gebruik dit voor concepten zoals project, result, optout, consent, agenda, import, phone of klantcode."
        )
    )


class ValidateProjectTablesArgs(BaseModel):
    """Arguments for validating required columns across project tables."""

    database_name: str = Field(
        description=(
            "Naam van de projectdatabase om te controleren. "
            "Meestal CWEProjectData of CWEProjectData_Archive."
        )
    )
    table_names: list[str] = Field(
        description="Lijst met campagnetabellen die gecontroleerd moeten worden."
    )
    required_columns: list[str] = Field(
        description="Lijst met verplichte kolommen die in alle tabellen aanwezig moeten zijn."
    )


def _get_connection(database_name: str):
    """Create a pyodbc connection to the specified database."""
    import re as _re
    import pyodbc

    base_conn_str = os.getenv("MSSQL_CONN_STR", "")
    if not base_conn_str:
        raise ValueError("MSSQL_CONN_STR environment variable is not set")

    conn_str = _re.sub(
        r"Database=[^;]*",
        f"Database={database_name}",
        base_conn_str,
        count=1,
        flags=_re.IGNORECASE,
    )

    return pyodbc.connect(conn_str, timeout=15)


def _query_schema_tables(database_name: str) -> pd.DataFrame:
    """List all tables and views in a database."""
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
    """Get columns for a specific table."""
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


def _query_validate_table_columns(
    database_name: str,
    table_names: list[str],
    required_columns: list[str],
) -> pd.DataFrame:
    """Validate whether each table contains all required columns."""
    if not table_names:
        return pd.DataFrame(
            columns=["TABLE_NAME", "COLUMN_NAME", "HAS_COLUMN"]
        )

    conn = _get_connection(database_name)
    try:
        table_placeholders = ",".join(["?"] * len(table_names))
        col_placeholders = ",".join(["?"] * len(required_columns))
        query = f"""
        SELECT
            c.TABLE_NAME,
            c.COLUMN_NAME,
            1 AS HAS_COLUMN
        FROM INFORMATION_SCHEMA.COLUMNS c
        WHERE c.TABLE_NAME IN ({table_placeholders})
          AND c.COLUMN_NAME IN ({col_placeholders})
        ORDER BY c.TABLE_NAME, c.COLUMN_NAME
        """
        params = list(table_names) + list(required_columns)
        return pd.read_sql(query, conn, params=params)
    finally:
        conn.close()


def _search_tables_in_db(database_name: str, search_term: str) -> list[dict]:
    """Search tables and columns in one database."""
    results: list[dict] = []
    conn = _get_connection(database_name)
    try:
        table_query = f"""
        SELECT TOP {MAX_TABLE_MATCHES_PER_DB}
            TABLE_NAME, TABLE_TYPE
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME LIKE ?
          AND TABLE_TYPE IN ('BASE TABLE', 'VIEW')
        ORDER BY TABLE_NAME
        """
        tables_df = pd.read_sql(table_query, conn, params=[f"%{search_term}%"])
        for _, row in tables_df.iterrows():
            results.append(
                {
                    "Database": database_name,
                    "Tabel": row["TABLE_NAME"],
                    "Type": row["TABLE_TYPE"],
                    "Match": "tabelnaam",
                }
            )

        col_query = f"""
        SELECT TOP {MAX_COLUMN_MATCHES_PER_DB}
            c.TABLE_NAME,
            c.COLUMN_NAME,
            c.DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS c
        JOIN INFORMATION_SCHEMA.TABLES t
            ON c.TABLE_NAME = t.TABLE_NAME
           AND c.TABLE_SCHEMA = t.TABLE_SCHEMA
        WHERE c.COLUMN_NAME LIKE ?
          AND t.TABLE_TYPE IN ('BASE TABLE', 'VIEW')
        ORDER BY c.TABLE_NAME, c.COLUMN_NAME
        """
        cols_df = pd.read_sql(col_query, conn, params=[f"%{search_term}%"])
        for _, row in cols_df.iterrows():
            results.append(
                {
                    "Database": database_name,
                    "Tabel": row["TABLE_NAME"],
                    "Type": f"kolom: {row['COLUMN_NAME']} ({row['DATA_TYPE']})",
                    "Match": "kolomnaam",
                }
            )
    finally:
        conn.close()

    return results


def _summarize_search_results(all_results: list[dict]) -> str:
    """Build a compact grouped summary for the LLM."""
    table_matches: dict[str, list[str]] = defaultdict(list)
    col_matches: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    for r in all_results:
        db = r["Database"]
        tbl = r["Tabel"]
        if r["Match"] == "tabelnaam":
            table_matches[db].append(tbl)
        elif r["Match"] == "kolomnaam":
            col_matches[db][tbl].append(r["Type"].replace("kolom: ", ""))

    lines: list[str] = []

    for db in sorted(table_matches):
        tables = sorted(set(table_matches[db]))
        lines.append(f"\n[{db}] — {len(tables)} tabellen met naam-match:")
        shown = tables[:30]
        for t in shown:
            lines.append(f"  • {t}")
        if len(tables) > 30:
            lines.append(f"  ... en nog {len(tables) - 30} tabellen")

    for db in sorted(col_matches):
        tables_in_db = col_matches[db]
        total_cols = sum(len(v) for v in tables_in_db.values())
        lines.append(
            f"\n[{db}] — kolom-matches in {len(tables_in_db)} tabellen ({total_cols} totaal):"
        )
        shown_tables = sorted(tables_in_db)[:MAX_SEARCH_RESULTS_FOR_LLM]
        for tbl in shown_tables:
            cols = sorted(set(tables_in_db[tbl]))
            cols_str = ", ".join(cols[:5])
            if len(cols) > 5:
                cols_str += f" (+{len(cols) - 5} meer)"
            lines.append(f"  • {tbl}: {cols_str}")

    if not lines:
        return "Geen resultaten."

    return "\n".join(lines)


class GetTableSchemaInfoTool(Tool[GetSchemaInfoArgs]):
    """Tool to inspect database schema dynamically."""

    @property
    def name(self) -> str:
        return "get_table_schema_info"

    @property
    def description(self) -> str:
        return (
            "Haal schema-informatie op van een database of specifieke tabel. "
            "Gebruik dit als je niet zeker weet welke tabellen of kolommen beschikbaar zijn, "
            "vooral bij CWESystemConfig, CWESystemData of minder gebruikelijke projectvelden."
        )

    def get_args_schema(self) -> Type[GetSchemaInfoArgs]:
        return GetSchemaInfoArgs

    async def execute(
        self,
        context: ToolContext,
        args: GetSchemaInfoArgs,
    ) -> ToolResult:
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
                    simple_component=SimpleTextComponent(text="Database niet beschikbaar."),
                ),
            )

        try:
            if not args.table_name and db in ("CWEProjectData", "CWEProjectData_Archive"):
                redirect_msg = (
                    f"[{db}] bevat veel campagnetabellen. "
                    f"Gebruik voor gerichte tabelkeuze liever `search_tables_across_databases` "
                    f"of een SQL-query op INFORMATION_SCHEMA.TABLES met klantcode of periodefilter. "
                    f"Gebruik `get_table_schema_info` hier vooral voor een specifieke tabel."
                )
                return ToolResult(
                    success=True,
                    result_for_llm=redirect_msg,
                    ui_component=UiComponent(
                        rich_component=StatusCardComponent(
                            title="Analyse wordt voorbereid",
                            status="info",
                            description="Relevante campagnes worden geselecteerd.",
                            icon="ℹ️",
                        ),
                        simple_component=SimpleTextComponent(
                            text="Relevante campagnes worden geselecteerd."
                        ),
                    ),
                )

            if args.table_name:
                df = await asyncio.to_thread(_query_schema_columns, db, args.table_name)

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
                            simple_component=SimpleTextComponent(text="Tabel niet gevonden."),
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
                        simple_component=SimpleTextComponent(
                            text=f"Schema opgehaald voor [{db}].[dbo].[{args.table_name}]."
                        ),
                    ),
                )

            df = await asyncio.to_thread(_query_schema_tables, db)

            total = len(df)
            shown_df = df.head(MAX_TABLES_FOR_LLM)
            result_text = f"Tabellen in [{db}] ({total} totaal):\n\n"
            result_text += shown_df.to_string(index=False)
            if total > MAX_TABLES_FOR_LLM:
                result_text += (
                    f"\n\n... en nog {total - MAX_TABLES_FOR_LLM} tabellen "
                    f"(gebruik search_tables_across_databases voor gerichter zoeken)"
                )

            return ToolResult(
                success=True,
                result_for_llm=result_text,
                ui_component=UiComponent(
                    rich_component=DataFrameComponent.from_records(
                        records=df.to_dict("records"),
                        title=f"Tabellen in [{db}]",
                        description=f"{len(df)} tabellen/views",
                    ),
                    simple_component=SimpleTextComponent(
                        text=f"Tabellijst opgehaald voor [{db}]."
                    ),
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
                        description="Het schema kon niet worden opgehaald.",
                        icon="❌",
                    ),
                    simple_component=SimpleTextComponent(text="Schema ophalen mislukt."),
                ),
                error=str(e),
            )


class SearchTablesAcrossDatabasesTool(Tool[SearchTablesArgs]):
    """Tool to search for tables and columns across all 6 databases."""

    @property
    def name(self) -> str:
        return "search_tables_across_databases"

    @property
    def description(self) -> str:
        return (
            "Zoek naar tabellen en kolommen over alle 6 databases heen. "
            "Gebruik dit als je niet zeker weet in welke database een concept, veld of tabel staat. "
            "Geschikt voor zoeken op tabelnaam, kolomnaam, klantcode of termen zoals result, optout, consent, agenda of import."
        )

    def get_args_schema(self) -> Type[SearchTablesArgs]:
        return SearchTablesArgs

    async def execute(
        self,
        context: ToolContext,
        args: SearchTablesArgs,
    ) -> ToolResult:
        search = args.search_term.strip()
        all_results: list[dict] = []

        if not search:
            msg = "Lege zoekterm is niet toegestaan."
            return ToolResult(
                success=False,
                result_for_llm=msg,
                ui_component=UiComponent(
                    rich_component=StatusCardComponent(
                        title="Ongeldige zoekterm",
                        status="warning",
                        description=msg,
                        icon="⚠️",
                    ),
                    simple_component=SimpleTextComponent(text="Ongeldige zoekterm."),
                ),
            )

        for db_name in sorted(ALLOWED_DATABASES):
            try:
                results = await asyncio.to_thread(_search_tables_in_db, db_name, search)
                all_results.extend(results)
            except Exception as e:
                logger.warning("Zoeken in [%s] mislukt: %s", db_name, e)
                all_results.append(
                    {
                        "Database": db_name,
                        "Tabel": f"FOUT: {str(e)[:80]}",
                        "Type": "error",
                        "Match": "error",
                    }
                )

        non_error_results = [r for r in all_results if r["Match"] != "error"]

        if not non_error_results:
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
                    simple_component=SimpleTextComponent(text="Geen resultaten gevonden."),
                ),
            )

        summary_text = (
            f"Zoekresultaten voor '{search}' "
            f"({len(non_error_results)} matches over {len(ALLOWED_DATABASES)} databases):\n"
        )
        summary_text += _summarize_search_results(non_error_results)

        return ToolResult(
            success=True,
            result_for_llm=summary_text,
            ui_component=UiComponent(
                rich_component=DataFrameComponent.from_records(
                    records=all_results,
                    title=f"Zoekresultaten: '{search}'",
                    description=f"{len(non_error_results)} resultaten over {len(ALLOWED_DATABASES)} databases",
                ),
                simple_component=SimpleTextComponent(
                    text=f"{len(non_error_results)} zoekresultaten gevonden."
                ),
            ),
        )


class ValidateProjectTablesForColumnsTool(Tool[ValidateProjectTablesArgs]):
    """Validate that selected project tables all contain required columns."""

    @property
    def name(self) -> str:
        return "validate_project_tables_for_columns"

    @property
    def description(self) -> str:
        return (
            "Controleer of geselecteerde campagnetabellen allemaal dezelfde verplichte kolommen bevatten. "
            "Gebruik dit voordat je meerdere projecttabellen combineert in één query."
        )

    def get_args_schema(self) -> Type[ValidateProjectTablesArgs]:
        return ValidateProjectTablesArgs

    async def execute(
        self,
        context: ToolContext,
        args: ValidateProjectTablesArgs,
    ) -> ToolResult:
        db = args.database_name
        table_names = [t.strip() for t in args.table_names if t.strip()]
        required_columns = [c.strip() for c in args.required_columns if c.strip()]

        if db not in ALLOWED_DATABASES:
            msg = f"Ongeldige database: '{db}'."
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
                    simple_component=SimpleTextComponent(text="Database niet beschikbaar."),
                ),
            )

        if not table_names:
            msg = "Geen tabellen opgegeven voor validatie."
            return ToolResult(
                success=False,
                result_for_llm=msg,
                ui_component=UiComponent(
                    rich_component=StatusCardComponent(
                        title="Geen tabellen opgegeven",
                        status="warning",
                        description=msg,
                        icon="⚠️",
                    ),
                    simple_component=SimpleTextComponent(text="Geen tabellen opgegeven."),
                ),
            )

        if not required_columns:
            msg = "Geen verplichte kolommen opgegeven voor validatie."
            return ToolResult(
                success=False,
                result_for_llm=msg,
                ui_component=UiComponent(
                    rich_component=StatusCardComponent(
                        title="Geen kolommen opgegeven",
                        status="warning",
                        description=msg,
                        icon="⚠️",
                    ),
                    simple_component=SimpleTextComponent(text="Geen kolommen opgegeven."),
                ),
            )

        try:
            df = await asyncio.to_thread(
                _query_validate_table_columns,
                db,
                table_names,
                required_columns,
            )

            found_map: dict[str, set[str]] = {t: set() for t in table_names}
            for _, row in df.iterrows():
                found_map[row["TABLE_NAME"]].add(row["COLUMN_NAME"])

            records: list[dict] = []
            valid_tables: list[str] = []
            invalid_tables: list[str] = []

            for table_name in table_names:
                found = found_map.get(table_name, set())
                missing = sorted(set(required_columns) - found)
                is_valid = len(missing) == 0
                if is_valid:
                    valid_tables.append(table_name)
                else:
                    invalid_tables.append(table_name)

                records.append(
                    {
                        "Database": db,
                        "Tabel": table_name,
                        "Valid": "ja" if is_valid else "nee",
                        "MissingColumns": ", ".join(missing) if missing else "",
                        "PresentColumns": ", ".join(sorted(found)),
                    }
                )

            result_lines = [
                f"Validatie van projecttabellen in [{db}]",
                f"Vereiste kolommen: {', '.join(required_columns)}",
                f"Geldige tabellen ({len(valid_tables)}): {', '.join(valid_tables) if valid_tables else '(geen)'}",
                f"Ongeldige tabellen ({len(invalid_tables)}): {', '.join(invalid_tables) if invalid_tables else '(geen)'}",
                "",
                "Details per tabel:",
            ]
            for rec in records:
                if rec["Valid"] == "ja":
                    result_lines.append(f"- {rec['Tabel']}: geldig")
                else:
                    result_lines.append(
                        f"- {rec['Tabel']}: ongeldig, ontbreekt: {rec['MissingColumns']}"
                    )

            result_text = "\n".join(result_lines)

            return ToolResult(
                success=True,
                result_for_llm=result_text,
                ui_component=UiComponent(
                    rich_component=DataFrameComponent.from_records(
                        records=records,
                        title="Tabelvalidatie voor analyse",
                        description=(
                            f"{len(valid_tables)} geldig, {len(invalid_tables)} ongeldig"
                        ),
                    ),
                    simple_component=SimpleTextComponent(
                        text=(
                            f"Tabelvalidatie voltooid: "
                            f"{len(valid_tables)} geldig, {len(invalid_tables)} ongeldig."
                        )
                    ),
                ),
            )

        except Exception as e:
            logger.exception("Validatie van projecttabellen mislukt voor [%s]", db)
            msg = f"Fout bij valideren van tabellen in [{db}]: {str(e)}"
            return ToolResult(
                success=False,
                result_for_llm=msg,
                ui_component=UiComponent(
                    rich_component=StatusCardComponent(
                        title="Validatie mislukt",
                        status="error",
                        description="De tabelvalidatie kon niet worden uitgevoerd.",
                        icon="❌",
                    ),
                    simple_component=SimpleTextComponent(text="Validatie mislukt."),
                ),
                error=str(e),
            )


# ---------------------------------------------------------------------------
# Web search
# ---------------------------------------------------------------------------


class WebSearchArgs(BaseModel):
    """Arguments for searching the web via DuckDuckGo."""

    query: str = Field(
        description=(
            "De zoekterm om op het web te zoeken naar actuele informatie. "
            "Gebruik dit voor vragen over nieuws, regelgeving, marktinformatie "
            "of andere actuele onderwerpen die niet in de databases staan."
        )
    )


class WebSearchTool(Tool[WebSearchArgs]):
    """Free web search via DuckDuckGo — no API key required."""

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return (
            "Zoek actuele informatie op het web via DuckDuckGo. "
            "Gebruik dit voor vragen over nieuws, wet- en regelgeving, marktinformatie "
            "of andere actuele onderwerpen die niet in de interne databases beschikbaar zijn."
        )

    def get_args_schema(self) -> Type[WebSearchArgs]:
        return WebSearchArgs

    async def execute(self, context: ToolContext, args: WebSearchArgs) -> ToolResult:
        from duckduckgo_search import DDGS

        def _search() -> list[dict]:
            with DDGS() as ddgs:
                return list(ddgs.text(args.query, max_results=5))

        try:
            results = await asyncio.to_thread(_search)
        except Exception as exc:
            logger.exception("Web search failed for query: %s", args.query)
            msg = f"Zoekfout: {exc}"
            return ToolResult(
                success=False,
                result_for_llm=msg,
                ui_component=UiComponent(
                    rich_component=StatusCardComponent(
                        title="Zoeken mislukt",
                        status="error",
                        description="De webzoekopdracht kon niet worden uitgevoerd.",
                        icon="❌",
                    ),
                    simple_component=SimpleTextComponent(text="Webzoekopdracht mislukt."),
                ),
                error=str(exc),
            )

        if not results:
            return ToolResult(
                success=True,
                result_for_llm="Geen resultaten gevonden voor deze zoekopdracht.",
                ui_component=UiComponent(
                    rich_component=StatusCardComponent(
                        title="Geen resultaten",
                        status="warning",
                        description=f'Geen webresultaten voor: "{args.query}"',
                        icon="🔍",
                    ),
                    simple_component=SimpleTextComponent(text="Geen webresultaten gevonden."),
                ),
            )

        text = "\n\n".join(
            f"**{r.get('title', '').strip()}**\n{r.get('body', '').strip()}\n{r.get('href', '')}"
            for r in results
        )

        return ToolResult(
            success=True,
            result_for_llm=text,
            ui_component=UiComponent(
                rich_component=StatusCardComponent(
                    title="Webzoekresultaten",
                    status="success",
                    description=f'{len(results)} resultaten voor: "{args.query}"',
                    icon="🌐",
                ),
                simple_component=SimpleTextComponent(
                    text=f"Webzoekopdracht voltooid: {len(results)} resultaten."
                ),
            ),
        )