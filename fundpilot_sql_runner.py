"""
Read-only SQL runner wrapper for FundPilot.

Wraps a SqlRunner to enforce read-only access (SELECT only) and adds
safety limits to prevent excessive result sets.
"""

from __future__ import annotations

import re
from typing import Optional

import pandas as pd
import sqlparse

from vanna.capabilities.sql_runner import SqlRunner, RunSqlToolArgs
from vanna.core.tool import ToolContext


# SQL statements that are explicitly forbidden
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
    "xp_",
    "sp_",
}


class ReadOnlySqlRunner(SqlRunner):
    """SQL runner wrapper that enforces read-only access.

    Wraps any SqlRunner implementation and validates that only SELECT
    statements are executed. Blocks all write/DDL/admin operations.

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
        """Validate and execute SQL query.

        Raises:
            ValueError: If the query contains forbidden operations.
        """
        sql = args.sql.strip()

        # Validate the SQL is read-only
        self._validate_read_only(sql)

        # Optionally inject TOP limit if not already present
        if self._max_rows and not self._has_top_clause(sql):
            sql = self._inject_top_limit(sql)
            args = RunSqlToolArgs(sql=sql)

        return await self._inner.run_sql(args, context)

    def _validate_read_only(self, sql: str) -> None:
        """Validate that the SQL only contains SELECT statements."""
        # Parse the SQL
        parsed = sqlparse.parse(sql)

        if not parsed:
            raise ValueError("Ongeldige SQL: lege query.")

        for statement in parsed:
            # Get the statement type
            stmt_type = statement.get_type()

            # Only SELECT and UNKNOWN (for complex queries) are allowed
            # UNKNOWN can happen with CTEs and other complex patterns
            if stmt_type and stmt_type not in ("SELECT", "UNKNOWN"):
                raise ValueError(
                    f"❌ Alleen SELECT-query's zijn toegestaan. "
                    f"Een {stmt_type}-statement is geblokkeerd. "
                    f"Dit systeem is uitsluitend bedoeld voor het lezen van data."
                )

            # Additional check: scan all tokens for forbidden keywords
            sql_upper = sql.upper()
            for keyword in FORBIDDEN_KEYWORDS:
                # Use word boundary matching to avoid false positives
                # e.g., "INSERT" should match but "INSERTING" in a column name shouldn't
                pattern = rf'\b{re.escape(keyword)}\b'
                if re.search(pattern, sql_upper):
                    # Allow sp_ and xp_ only inside string literals
                    if keyword in ("sp_", "xp_"):
                        # Simple check — if it's inside quotes, skip
                        idx = sql_upper.find(keyword)
                        before = sql[:idx]
                        if before.count("'") % 2 == 1:
                            continue
                    raise ValueError(
                        f"❌ Het gebruik van '{keyword}' is niet toegestaan. "
                        f"Dit systeem ondersteunt alleen SELECT-query's voor data-analyse."
                    )

    @staticmethod
    def _has_top_clause(sql: str) -> bool:
        """Check if the SQL already has a TOP clause."""
        return bool(re.search(r'\bTOP\s+\d+', sql, re.IGNORECASE))

    def _inject_top_limit(self, sql: str) -> str:
        """Inject TOP N into a SELECT statement if not already present."""
        # Handle CTEs (WITH ... AS ...) — inject into the final SELECT
        # Simple approach: find the last SELECT and inject TOP after it
        pattern = r'(?i)\bSELECT\s+(DISTINCT\s+)?'

        def _add_top(match):
            distinct = match.group(1) or ""
            return f"SELECT {distinct}TOP {self._max_rows} "

        # Only replace the first SELECT (or the main one)
        result = re.sub(pattern, _add_top, sql, count=1)
        return result
