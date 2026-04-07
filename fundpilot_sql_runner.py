"""
Read-only SQL runner wrapper for FundPilot.

Wraps a SqlRunner to enforce read-only access (SELECT only), adds
safety limits to prevent excessive result sets, and normalizes
Teleknowledge object naming to always use three-part naming:
[Database].[dbo].[Table]
"""

from __future__ import annotations

import re
from typing import Optional

import pandas as pd
import sqlparse

from vanna.capabilities.sql_runner import SqlRunner, RunSqlToolArgs
from vanna.core.tool import ToolContext


# Keywords that must match as whole words (word-boundary on both sides)
FORBIDDEN_KEYWORDS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "EXEC",
    "EXECUTE",
    "MERGE",
    "GRANT",
    "REVOKE",
    "DENY",
    "BACKUP",
    "RESTORE",
    "DBCC",
    "BULK",
    "OPENROWSET",
    "OPENDATASOURCE",
}

# Prefixes that should block any token starting with them (e.g. SP_EXECUTESQL)
FORBIDDEN_PREFIXES = {"XP_", "SP_"}

KNOWN_DATABASES = {
    "CWESystemConfig",
    "CWESystemData",
    "CWEProjectData",
    "CWESystemConfig_Archive",
    "CWESystemData_Archive",
    "CWEProjectData_Archive",
}


class ReadOnlySqlRunner(SqlRunner):
    """SQL runner wrapper that enforces read-only access.

    Wraps any SqlRunner implementation and validates that only SELECT
    statements are executed. Blocks all write/DDL/admin operations.

    Extra behavior:
    - Normalizes two-part Teleknowledge references like [DB].[Table]
      into [DB].[dbo].[Table]
    - Keeps valid three-part names unchanged
    - Injects TOP limit when needed

    Args:
        inner: The actual SqlRunner to delegate to after validation.
        max_rows: Maximum number of rows to return (default: 10000).
                  Set to None to disable limit.
    """

    def __init__(self, inner: SqlRunner, max_rows: Optional[int] = 10000):
        self._inner = inner
        self._max_rows = max_rows

    async def run_sql(
        self, args: RunSqlToolArgs, context: ToolContext
    ) -> pd.DataFrame:
        """Validate, normalize and execute SQL query.

        Raises:
            ValueError: If the query contains forbidden operations.
        """
        sql = args.sql.strip()

        self._validate_read_only(sql)

        sql = self._normalize_teleknowledge_object_names(sql)

        self._validate_no_invalid_two_part_names(sql)

        if self._max_rows and not self._has_top_clause(sql):
            sql = self._inject_top_limit(sql)

        args = RunSqlToolArgs(sql=sql)
        return await self._inner.run_sql(args, context)

    def _validate_read_only(self, sql: str) -> None:
        """Validate that the SQL only contains SELECT statements."""
        parsed = sqlparse.parse(sql)

        if not parsed:
            raise ValueError("Ongeldige SQL: lege query.")

        for statement in parsed:
            stmt_type = statement.get_type()

            if stmt_type and stmt_type not in ("SELECT", "UNKNOWN"):
                raise ValueError(
                    f"❌ Alleen SELECT-query's zijn toegestaan. "
                    f"Een {stmt_type}-statement is geblokkeerd. "
                    f"Dit systeem is uitsluitend bedoeld voor het lezen van data."
                )

            sql_upper = sql.upper()

            # Check whole-word forbidden keywords
            for keyword in FORBIDDEN_KEYWORDS:
                pattern = rf"\b{re.escape(keyword)}\b"
                if re.search(pattern, sql_upper):
                    raise ValueError(
                        f"❌ Het gebruik van '{keyword}' is niet toegestaan. "
                        f"Dit systeem ondersteunt alleen SELECT-query's voor data-analyse."
                    )

            # Check forbidden prefixes (e.g. SP_EXECUTESQL, XP_CMDSHELL)
            for prefix in FORBIDDEN_PREFIXES:
                pattern = rf"\b{re.escape(prefix)}\w+"
                for match in re.finditer(pattern, sql_upper):
                    # Skip occurrences inside string literals
                    before = sql_upper[: match.start()]
                    if before.count("'") % 2 == 1:
                        continue
                    raise ValueError(
                        f"❌ Het gebruik van '{prefix}...' is niet toegestaan. "
                        f"Dit systeem ondersteunt alleen SELECT-query's voor data-analyse."
                    )

    @staticmethod
    def _has_top_clause(sql: str) -> bool:
        """Check if the SQL already has a TOP clause."""
        return bool(re.search(r"\bTOP\s+\d+", sql, re.IGNORECASE))

    def _inject_top_limit(self, sql: str) -> str:
        """Inject TOP N into a SELECT statement if not already present."""
        pattern = r"(?i)\bSELECT\s+(DISTINCT\s+)?"

        def _add_top(match):
            distinct = match.group(1) or ""
            return f"SELECT {distinct}TOP {self._max_rows} "

        return re.sub(pattern, _add_top, sql, count=1)

    def _normalize_teleknowledge_object_names(self, sql: str) -> str:
        """Normalize [DB].[Table] to [DB].[dbo].[Table] for known databases.

        Leaves existing [DB].[schema].[Table] references untouched.
        Only rewrites exact two-part bracketed object names for known databases.
        """

        db_alternation = "|".join(re.escape(db) for db in sorted(KNOWN_DATABASES, key=len, reverse=True))

        # Match [Database].[Object] but NOT [Database].[schema].[Object]
        pattern = re.compile(
            rf"""
            \[
                (?P<db>{db_alternation})
            \]
            \.
            \[
                (?P<object>[^\]]+)
            \]
            (?!\s*\.\s*\[)   # not already followed by .[schema_or_table]
            """,
            re.IGNORECASE | re.VERBOSE,
        )

        def repl(match: re.Match) -> str:
            db = match.group("db")
            obj = match.group("object")
            return f"[{db}].[dbo].[{obj}]"

        return pattern.sub(repl, sql)

    def _validate_no_invalid_two_part_names(self, sql: str) -> None:
        """Block remaining obvious two-part names for known databases.

        This catches cases the normalizer missed and gives a clearer error.
        """
        db_alternation = "|".join(re.escape(db) for db in sorted(KNOWN_DATABASES, key=len, reverse=True))

        invalid_pattern = re.compile(
            rf"""
            \[
                ({db_alternation})
            \]
            \.
            \[
                ([^\]]+)
            \]
            (?!\s*\.\s*\[)
            """,
            re.IGNORECASE | re.VERBOSE,
        )

        remaining = invalid_pattern.findall(sql)
        if remaining:
            examples = ", ".join(f"[{db}].[{obj}]" for db, obj in remaining[:5])
            raise ValueError(
                "❌ Query gebruikt ongeldige tabelverwijzingen zonder schema. "
                "Gebruik altijd exact: [Database].[dbo].[Tabel]. "
                f"Gevonden: {examples}"
            )