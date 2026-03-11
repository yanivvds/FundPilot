"""
Schema extraction script for all Teleknowledge Connect databases.

Connects to each of the 6 databases and extracts complete schema information
including tables, columns, data types, primary keys, foreign keys, and row counts.

Output:
  - schema_cache/all_schemas.json   (structured JSON)
  - schema_cache/schema_docs.md     (human-readable Markdown)

Usage:
    python scripts/extract_schemas.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    import pyodbc
    import pandas as pd
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Ontbrekende dependency: {e}")
    print("   Installeer met: pip install pyodbc pandas python-dotenv")
    sys.exit(1)


# ── Database definitions ─────────────────────────────────────────────────

DATABASES = {
    "CWESystemConfig": {
        "env_key": "MSSQL_CONN_STR_CONFIG",
        "description": "Configuratie en structurele informatie: projecten, werkgroepen, gebruikers, resultaatcodes, verbindingen, systeeminstellingen.",
    },
    "CWESystemData": {
        "env_key": "MSSQL_CONN_STR_DATA",
        "description": "Operationele en runtime gegevens: belgeschiedenis, AI-resultaten, agentactiviteit, gewerkte uren, ACD-data, operationele prestaties.",
    },
    "CWEProjectData": {
        "env_key": "MSSQL_CONN_STR_PROJECT",
        "description": "Klant- en projectspecifieke gegevens: donordata, klantrecords, campagneresultaten, projectresultaten, acquisitiedata.",
    },
    "CWESystemConfig_Archive": {
        "env_key": "MSSQL_CONN_STR_CONFIG_ARCHIVE",
        "description": "Archief van CWESystemConfig — historische configuratiegegevens.",
    },
    "CWESystemData_Archive": {
        "env_key": "MSSQL_CONN_STR_DATA_ARCHIVE",
        "description": "Archief van CWESystemData — historische operationele gegevens.",
    },
    "CWEProjectData_Archive": {
        "env_key": "MSSQL_CONN_STR_PROJECT_ARCHIVE",
        "description": "Archief van CWEProjectData — historische klant- en projectgegevens.",
    },
    "ProjectInfoDB": {
        "env_key": "MSSQL_CONN_STR_PROJECT_DESCRIPTIONS",
        "description": "AI-verrijkte projectinformatie: projectcode, bedrijfsnaam, projecttype, AI-bedrijfsomschrijving, typische donor, categorieën en betrouwbaarheidsscore.",
    },
}


# ── SQL queries ──────────────────────────────────────────────────────────

TABLES_QUERY = """
SELECT 
    t.TABLE_SCHEMA,
    t.TABLE_NAME,
    t.TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES t
WHERE t.TABLE_TYPE IN ('BASE TABLE', 'VIEW')
ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME
"""

COLUMNS_QUERY = """
SELECT 
    c.TABLE_SCHEMA,
    c.TABLE_NAME,
    c.COLUMN_NAME,
    c.DATA_TYPE,
    c.CHARACTER_MAXIMUM_LENGTH,
    c.NUMERIC_PRECISION,
    c.NUMERIC_SCALE,
    c.IS_NULLABLE,
    c.COLUMN_DEFAULT,
    c.ORDINAL_POSITION
FROM INFORMATION_SCHEMA.COLUMNS c
ORDER BY c.TABLE_SCHEMA, c.TABLE_NAME, c.ORDINAL_POSITION
"""

PRIMARY_KEYS_QUERY = """
SELECT 
    tc.TABLE_SCHEMA,
    tc.TABLE_NAME,
    kcu.COLUMN_NAME,
    tc.CONSTRAINT_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu 
    ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
    AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
ORDER BY tc.TABLE_SCHEMA, tc.TABLE_NAME, kcu.ORDINAL_POSITION
"""

FOREIGN_KEYS_QUERY = """
SELECT 
    tc.TABLE_SCHEMA,
    tc.TABLE_NAME,
    kcu.COLUMN_NAME,
    ccu.TABLE_SCHEMA AS REFERENCED_SCHEMA,
    ccu.TABLE_NAME AS REFERENCED_TABLE,
    ccu.COLUMN_NAME AS REFERENCED_COLUMN,
    tc.CONSTRAINT_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu 
    ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
    AND tc.TABLE_SCHEMA = kcu.TABLE_SCHEMA
JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE ccu 
    ON tc.CONSTRAINT_NAME = ccu.CONSTRAINT_NAME
WHERE tc.CONSTRAINT_TYPE = 'FOREIGN KEY'
ORDER BY tc.TABLE_SCHEMA, tc.TABLE_NAME
"""

ROW_COUNTS_QUERY = """
SELECT 
    s.name AS TABLE_SCHEMA,
    t.name AS TABLE_NAME,
    p.rows AS ROW_COUNT
FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id
JOIN sys.partitions p ON t.object_id = p.object_id AND p.index_id IN (0, 1)
ORDER BY s.name, t.name
"""


def connect_to_database(conn_str: str) -> pyodbc.Connection:
    """Create a connection to a SQL Server database."""
    # Remove surrounding quotes if present
    conn_str = conn_str.strip().strip('"').strip("'")
    return pyodbc.connect(conn_str, timeout=30)


def extract_schema(db_name: str, conn_str: str) -> Dict[str, Any]:
    """Extract complete schema information from a single database."""
    print(f"  📋 Extracting schema from {db_name}...")

    try:
        conn = connect_to_database(conn_str)
    except Exception as e:
        print(f"  ❌ Kan niet verbinden met {db_name}: {e}")
        return {"error": str(e), "tables": {}}

    schema: Dict[str, Any] = {"tables": {}, "extracted_at": datetime.now().isoformat()}

    try:
        # 1. Get tables
        tables_df = pd.read_sql(TABLES_QUERY, conn)
        print(f"     Gevonden: {len(tables_df)} tabellen/views")

        for _, row in tables_df.iterrows():
            key = f"{row['TABLE_SCHEMA']}.{row['TABLE_NAME']}"
            schema["tables"][key] = {
                "schema": row["TABLE_SCHEMA"],
                "name": row["TABLE_NAME"],
                "type": row["TABLE_TYPE"],
                "columns": [],
                "primary_keys": [],
                "foreign_keys": [],
                "row_count": None,
            }

        # 2. Get columns
        columns_df = pd.read_sql(COLUMNS_QUERY, conn)
        for _, row in columns_df.iterrows():
            key = f"{row['TABLE_SCHEMA']}.{row['TABLE_NAME']}"
            if key in schema["tables"]:
                col_info = {
                    "name": row["COLUMN_NAME"],
                    "data_type": row["DATA_TYPE"],
                    "max_length": (
                        int(row["CHARACTER_MAXIMUM_LENGTH"])
                        if pd.notna(row["CHARACTER_MAXIMUM_LENGTH"])
                        else None
                    ),
                    "precision": (
                        int(row["NUMERIC_PRECISION"])
                        if pd.notna(row["NUMERIC_PRECISION"])
                        else None
                    ),
                    "scale": (
                        int(row["NUMERIC_SCALE"])
                        if pd.notna(row["NUMERIC_SCALE"])
                        else None
                    ),
                    "nullable": row["IS_NULLABLE"] == "YES",
                    "default": row["COLUMN_DEFAULT"],
                    "ordinal": int(row["ORDINAL_POSITION"]),
                }
                schema["tables"][key]["columns"].append(col_info)

        # 3. Get primary keys
        try:
            pk_df = pd.read_sql(PRIMARY_KEYS_QUERY, conn)
            for _, row in pk_df.iterrows():
                key = f"{row['TABLE_SCHEMA']}.{row['TABLE_NAME']}"
                if key in schema["tables"]:
                    schema["tables"][key]["primary_keys"].append(row["COLUMN_NAME"])
        except Exception as e:
            print(f"     ⚠️  Primary keys ophalen mislukt: {e}")

        # 4. Get foreign keys
        try:
            fk_df = pd.read_sql(FOREIGN_KEYS_QUERY, conn)
            for _, row in fk_df.iterrows():
                key = f"{row['TABLE_SCHEMA']}.{row['TABLE_NAME']}"
                if key in schema["tables"]:
                    fk_info = {
                        "column": row["COLUMN_NAME"],
                        "references_schema": row["REFERENCED_SCHEMA"],
                        "references_table": row["REFERENCED_TABLE"],
                        "references_column": row["REFERENCED_COLUMN"],
                        "constraint_name": row["CONSTRAINT_NAME"],
                    }
                    schema["tables"][key]["foreign_keys"].append(fk_info)
        except Exception as e:
            print(f"     ⚠️  Foreign keys ophalen mislukt: {e}")

        # 5. Get row counts
        try:
            rc_df = pd.read_sql(ROW_COUNTS_QUERY, conn)
            for _, row in rc_df.iterrows():
                key = f"{row['TABLE_SCHEMA']}.{row['TABLE_NAME']}"
                if key in schema["tables"]:
                    schema["tables"][key]["row_count"] = int(row["ROW_COUNT"])
        except Exception as e:
            print(f"     ⚠️  Rij-aantallen ophalen mislukt: {e}")

    finally:
        conn.close()

    table_count = len(schema["tables"])
    total_cols = sum(len(t["columns"]) for t in schema["tables"].values())
    print(f"     ✅ {table_count} tabellen, {total_cols} kolommen geëxtraheerd")

    return schema


def generate_markdown(all_schemas: Dict[str, Any]) -> str:
    """Generate human-readable Markdown documentation from extracted schemas."""
    lines: List[str] = []
    lines.append("# Teleknowledge Connect — Database Schema Documentatie")
    lines.append("")
    lines.append(f"*Gegenereerd op: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    lines.append("")
    lines.append("---")
    lines.append("")

    for db_name, db_info in all_schemas.items():
        desc = DATABASES.get(db_name, {}).get("description", "")
        schema_data = db_info.get("schema", {})
        tables = schema_data.get("tables", {})

        lines.append(f"## {db_name}")
        lines.append("")
        if desc:
            lines.append(f"**Doel:** {desc}")
            lines.append("")

        if "error" in schema_data:
            lines.append(f"⚠️ Fout bij extractie: {schema_data['error']}")
            lines.append("")
            continue

        lines.append(f"**Aantal tabellen:** {len(tables)}")
        total_rows = sum(
            t.get("row_count", 0) or 0
            for t in tables.values()
            if t.get("type") == "BASE TABLE"
        )
        lines.append(f"**Totaal records:** {total_rows:,}")
        lines.append("")

        for table_key, table_info in sorted(tables.items()):
            table_type = "VIEW" if table_info["type"] == "VIEW" else "TABLE"
            row_count = table_info.get("row_count")
            rc_str = f" ({row_count:,} rijen)" if row_count is not None else ""

            lines.append(
                f"### [{db_name}].[{table_info['schema']}].[{table_info['name']}] — {table_type}{rc_str}"
            )
            lines.append("")

            # Primary keys
            if table_info["primary_keys"]:
                pk_str = ", ".join(table_info["primary_keys"])
                lines.append(f"**Primary Key:** {pk_str}")
                lines.append("")

            # Columns table
            if table_info["columns"]:
                lines.append("| Kolom | Type | Nullable | Standaard |")
                lines.append("|-------|------|----------|-----------|")
                for col in table_info["columns"]:
                    dtype = col["data_type"]
                    if col["max_length"] and col["max_length"] > 0:
                        dtype += f"({col['max_length']})"
                    elif col["precision"]:
                        dtype += f"({col['precision']}"
                        if col["scale"]:
                            dtype += f",{col['scale']}"
                        dtype += ")"
                    nullable = "✓" if col["nullable"] else "✗"
                    default = col["default"] or ""
                    lines.append(f"| {col['name']} | {dtype} | {nullable} | {default} |")
                lines.append("")

            # Foreign keys
            if table_info["foreign_keys"]:
                lines.append("**Foreign Keys:**")
                for fk in table_info["foreign_keys"]:
                    lines.append(
                        f"- `{fk['column']}` → `[{fk['references_schema']}].[{fk['references_table']}].[{fk['references_column']}]`"
                    )
                lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    """Main entry point — extract schemas from all 6 databases."""
    load_dotenv(dotenv_path=project_root / ".env")

    output_dir = project_root / "schema_cache"
    output_dir.mkdir(exist_ok=True)

    print("🔍 Teleknowledge Connect Schema Extractie")
    print("=" * 50)
    print()

    all_schemas: Dict[str, Any] = {}
    success_count = 0
    error_count = 0

    for db_name, db_config in DATABASES.items():
        conn_str = os.getenv(db_config["env_key"])
        if not conn_str:
            print(f"  ⚠️  {db_name}: Geen connectiestring gevonden ({db_config['env_key']})")
            all_schemas[db_name] = {
                "description": db_config["description"],
                "schema": {"error": f"Omgevingsvariabele {db_config['env_key']} niet ingesteld", "tables": {}},
            }
            error_count += 1
            continue

        schema = extract_schema(db_name, conn_str)
        all_schemas[db_name] = {
            "description": db_config["description"],
            "schema": schema,
        }

        if "error" not in schema:
            success_count += 1
        else:
            error_count += 1

        print()

    # Write JSON
    json_path = output_dir / "all_schemas.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_schemas, f, indent=2, default=str, ensure_ascii=False)
    print(f"📄 JSON opgeslagen: {json_path}")

    # Write Markdown
    md_path = output_dir / "schema_docs.md"
    md_content = generate_markdown(all_schemas)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"📄 Markdown opgeslagen: {md_path}")

    # Summary
    print()
    print("=" * 50)
    print(f"✅ Geslaagd: {success_count} databases")
    if error_count:
        print(f"❌ Mislukt: {error_count} databases")

    total_tables = sum(
        len(db.get("schema", {}).get("tables", {}))
        for db in all_schemas.values()
    )
    total_cols = sum(
        sum(len(t.get("columns", [])) for t in db.get("schema", {}).get("tables", {}).values())
        for db in all_schemas.values()
    )
    print(f"📊 Totaal: {total_tables} tabellen, {total_cols} kolommen over {success_count} databases")

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
