"""
Training pipeline for FundPilot multi-database agent.

Populates ChromaDB persistent memory with:
1. Schema information from all 6 databases
2. Domain knowledge documentation
3. Example question → SQL patterns for strategic use cases
4. Cross-database query patterns

Usage:
    python scripts/train_agent.py                  # Full training
    python scripts/train_agent.py --schema-only    # Only load schemas
    python scripts/train_agent.py --clear          # Clear and retrain

Requires:
    - schema_cache/all_schemas.json (run extract_schemas.py first)
    - docs/domain_knowledge.md
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ python-dotenv niet gevonden. Installeer met: pip install python-dotenv")
    sys.exit(1)


# ── Database descriptions ────────────────────────────────────────────────

DATABASE_DESCRIPTIONS = {
    "CWESystemConfig": (
        "CWESystemConfig bevat alle configuratie en structurele informatie van "
        "Teleknowledge Connect: projecten, werkgroepen, gebruikers, resultaatcodes, "
        "verbindingen en systeemconfiguratie."
    ),
    "CWESystemData": (
        "CWESystemData bevat alle operationele en runtime gegevens: belgeschiedenis, "
        "AI-uitkomsten, agentactiviteit, gewerkte uren, ACD-data en operationele "
        "prestatie-indicatoren."
    ),
    "CWEProjectData": (
        "CWEProjectData bevat alle klant- en projectspecifieke gegevens: donordata, "
        "klantrecords, campagneresultaten, projectresultaten, acquisitiedata en "
        "donateurprofielen."
    ),
    "CWESystemConfig_Archive": (
        "CWESystemConfig_Archive is het archief van CWESystemConfig met historische "
        "configuratiegegevens. Gebruik bij historische analyse en trendvergelijkingen."
    ),
    "CWESystemData_Archive": (
        "CWESystemData_Archive is het archief van CWESystemData met historische "
        "operationele gegevens. Gebruik bij langetermijn prestatieanalyse."
    ),
    "CWEProjectData_Archive": (
        "CWEProjectData_Archive is het archief van CWEProjectData met historische "
        "klant- en projectgegevens. Essentieel voor retentie- en LTV-analyse."
    ),
}


# ── Example Q&A pairs ───────────────────────────────────────────────────

EXAMPLE_PATTERNS = [
    {
        "question": "Hoeveel tabellen zitten er in elke database?",
        "tool_name": "run_sql",
        "args": {
            "sql": """
SELECT 'CWESystemConfig' AS DatabaseNaam, COUNT(*) AS AantalTabellen
FROM [CWESystemConfig].INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'
UNION ALL
SELECT 'CWESystemData', COUNT(*)
FROM [CWESystemData].INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'
UNION ALL
SELECT 'CWEProjectData', COUNT(*)
FROM [CWEProjectData].INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'
UNION ALL
SELECT 'CWESystemConfig_Archive', COUNT(*)
FROM [CWESystemConfig_Archive].INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'
UNION ALL
SELECT 'CWESystemData_Archive', COUNT(*)
FROM [CWESystemData_Archive].INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'
UNION ALL
SELECT 'CWEProjectData_Archive', COUNT(*)
FROM [CWEProjectData_Archive].INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY DatabaseNaam
""",
        },
    },
    {
        "question": "Welke project-tabellen zijn beschikbaar in CWEProjectData?",
        "tool_name": "run_sql",
        "args": {
            "sql": """
SELECT TABLE_NAME
FROM [CWEProjectData].INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME
""",
        },
    },
    {
        "question": "Retentie-analyse: welke donateurs blijven en welke haken af na 1, 3, 6 en 12 maanden?",
        "tool_name": "run_sql",
        "args": {
            "sql": """
WITH AllDonations AS (
    SELECT ID, CollectDate, Amount, Project_Code, ImportSource
    FROM [CWEProjectData].[dbo].[KLF2401] WITH (NOLOCK) WHERE CollectDate IS NOT NULL
    UNION ALL
    SELECT ID, CollectDate, Amount, Project_Code, ImportSource
    FROM [CWEProjectData].[dbo].[AZG2501] WITH (NOLOCK) WHERE CollectDate IS NOT NULL
    UNION ALL
    SELECT ID, CollectDate, Amount, Project_Code, ImportSource
    FROM [CWEProjectData].[dbo].[FSH2501] WITH (NOLOCK) WHERE CollectDate IS NOT NULL
    UNION ALL
    SELECT ID, CollectDate, Amount, Project_Code, ImportSource
    FROM [CWEProjectData].[dbo].[DAM2501] WITH (NOLOCK) WHERE CollectDate IS NOT NULL
    UNION ALL
    SELECT ID, CollectDate, Amount, Project_Code, ImportSource
    FROM [CWEProjectData].[dbo].[LDH2502] WITH (NOLOCK) WHERE CollectDate IS NOT NULL
),
FirstDonation AS (
    SELECT ID, MIN(CollectDate) AS first_date
    FROM AllDonations GROUP BY ID
),
Cohort AS (
    SELECT FORMAT(f.first_date, 'yyyy-MM') AS cohort, f.ID, f.first_date
    FROM FirstDonation f
)
SELECT
    c.cohort,
    COUNT(DISTINCT c.ID) AS cohort_size,
    COUNT(DISTINCT CASE WHEN d.CollectDate >= DATEADD(MONTH, 1, c.first_date) THEN c.ID END) AS retained_1m,
    CAST(COUNT(DISTINCT CASE WHEN d.CollectDate >= DATEADD(MONTH, 1, c.first_date) THEN c.ID END) AS FLOAT) / NULLIF(COUNT(DISTINCT c.ID), 0) * 100 AS pct_1m,
    COUNT(DISTINCT CASE WHEN d.CollectDate >= DATEADD(MONTH, 3, c.first_date) THEN c.ID END) AS retained_3m,
    CAST(COUNT(DISTINCT CASE WHEN d.CollectDate >= DATEADD(MONTH, 3, c.first_date) THEN c.ID END) AS FLOAT) / NULLIF(COUNT(DISTINCT c.ID), 0) * 100 AS pct_3m,
    COUNT(DISTINCT CASE WHEN d.CollectDate >= DATEADD(MONTH, 6, c.first_date) THEN c.ID END) AS retained_6m,
    CAST(COUNT(DISTINCT CASE WHEN d.CollectDate >= DATEADD(MONTH, 6, c.first_date) THEN c.ID END) AS FLOAT) / NULLIF(COUNT(DISTINCT c.ID), 0) * 100 AS pct_6m,
    COUNT(DISTINCT CASE WHEN d.CollectDate >= DATEADD(MONTH, 12, c.first_date) THEN c.ID END) AS retained_12m,
    CAST(COUNT(DISTINCT CASE WHEN d.CollectDate >= DATEADD(MONTH, 12, c.first_date) THEN c.ID END) AS FLOAT) / NULLIF(COUNT(DISTINCT c.ID), 0) * 100 AS pct_12m
FROM Cohort c
LEFT JOIN AllDonations d ON c.ID = d.ID AND d.CollectDate > c.first_date
GROUP BY c.cohort
ORDER BY c.cohort
""",
        },
    },
    {
        "question": "Herkomst beste donateurs: volume en waarde per kanaal/ImportSource",
        "tool_name": "run_sql",
        "args": {
            "sql": """
WITH AllDonors AS (
    SELECT ImportSource, Amount, Frequency, Project_Code, CollectDate, RecordStatus
    FROM [CWEProjectData].[dbo].[KLF2401] WITH (NOLOCK)
    UNION ALL
    SELECT ImportSource, Amount, Frequency, Project_Code, CollectDate, RecordStatus
    FROM [CWEProjectData].[dbo].[AZG2501] WITH (NOLOCK)
    UNION ALL
    SELECT ImportSource, Amount, Frequency, Project_Code, CollectDate, RecordStatus
    FROM [CWEProjectData].[dbo].[FSH2501] WITH (NOLOCK)
    UNION ALL
    SELECT ImportSource, Amount, Frequency, Project_Code, CollectDate, RecordStatus
    FROM [CWEProjectData].[dbo].[DAM2501] WITH (NOLOCK)
)
SELECT
    ImportSource AS Kanaal,
    COUNT(*) AS AantalDonateurs,
    SUM(Amount) AS TotaalBedrag,
    AVG(Amount) AS GemiddeldBedrag,
    COUNT(CASE WHEN Amount > 0 THEN 1 END) AS MetDonatie
FROM AllDonors
WHERE ImportSource IS NOT NULL AND ImportSource <> ''
GROUP BY ImportSource
ORDER BY TotaalBedrag DESC
""",
        },
    },
    {
        "question": "Campagne-effectiviteit: conversie en opbrengst per project",
        "tool_name": "run_sql",
        "args": {
            "sql": """
SELECT
    p.Project_Code,
    p.Project_Name,
    stats.TotaalRecords,
    stats.Conversies,
    CAST(stats.Conversies AS FLOAT) / NULLIF(stats.TotaalRecords, 0) * 100 AS ConversiePerc,
    stats.TotaalOpbrengst,
    stats.GemBedrag
FROM [CWESystemConfig].[dbo].[Project] p WITH (NOLOCK)
CROSS APPLY (
    SELECT COUNT(*) AS TotaalRecords,
           COUNT(CASE WHEN Amount > 0 THEN 1 END) AS Conversies,
           SUM(Amount) AS TotaalOpbrengst,
           AVG(CASE WHEN Amount > 0 THEN Amount END) AS GemBedrag
    FROM [CWEProjectData].[dbo].[KLF2401] WITH (NOLOCK)
    WHERE Project_Id = p.Project_ID
) stats
WHERE p.Project_Active = 1 AND stats.TotaalRecords > 0
ORDER BY stats.TotaalOpbrengst DESC
""",
        },
    },
    {
        "question": "Compliance-gezondheid: toestemmingen en opt-outs per project",
        "tool_name": "run_sql",
        "args": {
            "sql": """
SELECT
    Project_Code,
    COUNT(*) AS Totaal,
    SUM(CASE WHEN OptinTM = 1 THEN 1 ELSE 0 END) AS OptinTM,
    CAST(SUM(CASE WHEN OptinTM = 1 THEN 1 ELSE 0 END) AS FLOAT) / NULLIF(COUNT(*), 0) * 100 AS OptinTMPerc,
    SUM(CASE WHEN OptinEM = 1 THEN 1 ELSE 0 END) AS OptinEmail,
    SUM(CASE WHEN OptoutCompanyTM = 1 THEN 1 ELSE 0 END) AS OptoutTM
FROM [CWEProjectData].[dbo].[KLF2401] WITH (NOLOCK)
GROUP BY Project_Code
""",
        },
    },
    {
        "question": "Donateur-profiel: kenmerken van blijvers versus afhakers",
        "tool_name": "run_sql",
        "args": {
            "sql": """
WITH AllDonors AS (
    SELECT ID, Amount, Frequency, DonationPreference, Gender, City,
           CollectDate, ImportSource, DateOfBirth
    FROM [CWEProjectData].[dbo].[KLF2401] WITH (NOLOCK)
    UNION ALL
    SELECT ID, Amount, Frequency, DonationPreference, Gender, City,
           CollectDate, ImportSource, DateOfBirth
    FROM [CWEProjectData].[dbo].[AZG2501] WITH (NOLOCK)
),
FirstAndLast AS (
    SELECT ID, MIN(CollectDate) AS first_date, MAX(CollectDate) AS last_date,
           COUNT(*) AS donation_count, AVG(Amount) AS avg_amount
    FROM AllDonors WHERE CollectDate IS NOT NULL
    GROUP BY ID
)
SELECT
    CASE WHEN DATEDIFF(MONTH, first_date, last_date) >= 12 THEN 'Blijver (12m+)'
         WHEN DATEDIFF(MONTH, first_date, last_date) >= 6 THEN 'Medium (6-12m)'
         WHEN DATEDIFF(MONTH, first_date, last_date) >= 3 THEN 'Kortstondig (3-6m)'
         ELSE 'Afhaker (<3m)' END AS Categorie,
    COUNT(*) AS Aantal,
    AVG(avg_amount) AS GemBedrag,
    AVG(donation_count) AS GemAantalDonaties
FROM FirstAndLast
GROUP BY CASE WHEN DATEDIFF(MONTH, first_date, last_date) >= 12 THEN 'Blijver (12m+)'
              WHEN DATEDIFF(MONTH, first_date, last_date) >= 6 THEN 'Medium (6-12m)'
              WHEN DATEDIFF(MONTH, first_date, last_date) >= 3 THEN 'Kortstondig (3-6m)'
              ELSE 'Afhaker (<3m)' END
ORDER BY Aantal DESC
""",
        },
    },
]


async def train_agent(clear: bool = False, schema_only: bool = False):
    """Main training function."""
    load_dotenv(dotenv_path=project_root / ".env")

    # Import Vanna components
    try:
        from vanna.integrations.chromadb import ChromaAgentMemory
        from vanna.core.tool import ToolContext
        from vanna.core.user import User
    except ImportError as e:
        print(f"❌ Import fout: {e}")
        print("   Zorg dat vanna[chromadb] is geïnstalleerd.")
        sys.exit(1)

    # Set up ChromaDB
    persist_dir = os.getenv("CHROMADB_PERSIST_DIR", "./chromadb_data")
    memory = ChromaAgentMemory(
        persist_directory=persist_dir,
        collection_name="fundpilot_memory",
    )

    # Create a minimal tool context for saving memories
    dummy_user = User(id="trainer", email="trainer@fundpilot.local", group_memberships=["admin"])
    dummy_context = ToolContext(
        user=dummy_user,
        conversation_id="training",
        message_id="training",
    )

    if clear:
        print("🗑️  Geheugen wissen...")
        cleared = await memory.clear_memories(dummy_context)
        print(f"   {cleared} herinneringen gewist.")
        print()

    saved_count = 0

    # ── Phase 1: Load schema information ─────────────────────────────
    print("📋 Fase 1: Schema-informatie laden...")
    schema_file = project_root / "schema_cache" / "all_schemas.json"

    if schema_file.exists():
        with open(schema_file, "r", encoding="utf-8") as f:
            all_schemas = json.load(f)

        for db_name, db_info in all_schemas.items():
            description = db_info.get("description", "")
            schema_data = db_info.get("schema", {})
            tables = schema_data.get("tables", {})

            if "error" in schema_data:
                print(f"   ⚠️  {db_name}: overgeslagen (extractiefout)")
                continue

            # Save database description
            await memory.save_text_memory(
                content=f"Database {db_name}: {description}",
                context=dummy_context,
            )
            saved_count += 1

            # Save table-level summaries (batch per database)
            table_summaries = []
            for table_key, table_info in tables.items():
                cols = [c["name"] for c in table_info.get("columns", [])]
                col_str = ", ".join(cols[:20])  # First 20 columns
                if len(cols) > 20:
                    col_str += f" ... (+{len(cols) - 20} meer)"
                pks = table_info.get("primary_keys", [])
                pk_str = f" PK: {', '.join(pks)}" if pks else ""
                rc = table_info.get("row_count")
                rc_str = f" ({rc:,} rijen)" if rc is not None else ""

                table_summaries.append(
                    f"[{db_name}].[{table_info['schema']}].[{table_info['name']}]{rc_str}{pk_str}: {col_str}"
                )

            # Save in chunks of 5 tables per memory to balance granularity vs count
            chunk_size = 5
            for i in range(0, len(table_summaries), chunk_size):
                chunk = table_summaries[i : i + chunk_size]
                content = f"Tabelschema's in {db_name}:\n" + "\n".join(chunk)
                await memory.save_text_memory(content=content, context=dummy_context)
                saved_count += 1

            print(f"   ✅ {db_name}: {len(tables)} tabellen opgeslagen")

        # Save detailed column info for large/important tables
        for db_name, db_info in all_schemas.items():
            schema_data = db_info.get("schema", {})
            tables = schema_data.get("tables", {})

            for table_key, table_info in tables.items():
                # Only save detailed info for tables with > 5 columns
                columns = table_info.get("columns", [])
                if len(columns) > 5:
                    col_details = []
                    for col in columns:
                        dtype = col["data_type"]
                        if col.get("max_length") and col["max_length"] > 0:
                            dtype += f"({col['max_length']})"
                        nullable = "NULL" if col.get("nullable") else "NOT NULL"
                        col_details.append(f"  {col['name']} {dtype} {nullable}")

                    content = (
                        f"Gedetailleerde kolommen van [{db_name}].[{table_info['schema']}].[{table_info['name']}]:\n"
                        + "\n".join(col_details)
                    )
                    await memory.save_text_memory(content=content, context=dummy_context)
                    saved_count += 1
    else:
        print(f"   ⚠️  Schema bestand niet gevonden: {schema_file}")
        print("      Voer eerst uit: python scripts/extract_schemas.py")

    if schema_only:
        print(f"\n✅ Schema-training voltooid: {saved_count} herinneringen opgeslagen")
        return saved_count

    # ── Phase 2: Domain knowledge ────────────────────────────────────
    print("\n📚 Fase 2: Domeinkennis laden...")
    domain_file = project_root / "docs" / "domain_knowledge.md"

    if domain_file.exists():
        with open(domain_file, "r", encoding="utf-8") as f:
            domain_content = f.read()

        # Split into sections and save each as a separate memory
        sections = domain_content.split("\n---\n")
        for section in sections:
            section = section.strip()
            if section and len(section) > 50:
                # Further split very long sections
                if len(section) > 2000:
                    # Split by ## headers
                    subsections = section.split("\n## ")
                    for i, subsection in enumerate(subsections):
                        if subsection.strip() and len(subsection.strip()) > 50:
                            prefix = "## " if i > 0 else ""
                            await memory.save_text_memory(
                                content=prefix + subsection.strip(),
                                context=dummy_context,
                            )
                            saved_count += 1
                else:
                    await memory.save_text_memory(
                        content=section, context=dummy_context
                    )
                    saved_count += 1

        print(f"   ✅ Domeinkennis opgeslagen")
    else:
        print(f"   ⚠️  Domeinkennis bestand niet gevonden: {domain_file}")

    # ── Phase 3: Example patterns ────────────────────────────────────
    print("\n🎯 Fase 3: Voorbeeldpatronen laden...")

    for pattern in EXAMPLE_PATTERNS:
        await memory.save_tool_usage(
            question=pattern["question"],
            tool_name=pattern["tool_name"],
            args=pattern["args"],
            context=dummy_context,
            success=True,
            metadata={"source": "training"},
        )
        saved_count += 1
        print(f"   ✅ Patroon: {pattern['question'][:60]}...")

    # ── Phase 4: Cross-database patterns ─────────────────────────────
    print("\n🔗 Fase 4: Cross-database patronen laden...")

    cross_db_knowledge = [
        (
            "Om data van configuratie en operaties te combineren, JOIN altijd via "
            "[CWESystemConfig] en [CWESystemData] op gedeelde sleutels zoals ProjectID, "
            "WorkgroupID of UserID."
        ),
        (
            "Voor retentie-analyse: combineer [CWEProjectData] met [CWEProjectData_Archive] "
            "via UNION ALL. Filter op donatiedatum om de gewenste periode te selecteren."
        ),
        (
            "De archiefdatabases (_Archive) hebben dezelfde tabelstructuur als de primaire "
            "databases. Je kunt ze veilig combineren met UNION ALL."
        ),
        (
            "Om de kostprijs per donateur te berekenen: belminuten uit [CWESystemData], "
            "donateurgegevens uit [CWEProjectData], en projecttarieven uit [CWESystemConfig]."
        ),
        (
            "Gebruik ALTIJD three-part naming in queries: [DatabaseNaam].[dbo].[TabelNaam]. "
            "Dit is verplicht omdat queries over meerdere databases gaan."
        ),
        (
            "Als je niet weet welke tabel de gevraagde informatie bevat, gebruik dan "
            "de search_tables_across_databases tool om te zoeken over alle databases."
        ),
        (
            "Als je de kolommen van een specifieke tabel wilt zien, gebruik dan "
            "de get_table_schema_info tool met de databasenaam en tabelnaam."
        ),
    ]

    for knowledge in cross_db_knowledge:
        await memory.save_text_memory(content=knowledge, context=dummy_context)
        saved_count += 1

    print(f"   ✅ {len(cross_db_knowledge)} cross-database patronen opgeslagen")

    # ── Summary ──────────────────────────────────────────────────────
    print()
    print("=" * 50)
    print(f"✅ Training voltooid: {saved_count} herinneringen opgeslagen in ChromaDB")
    print(f"   Locatie: {os.path.abspath(persist_dir)}")

    return saved_count


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="FundPilot Agent Training Pipeline")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Wis eerst alle bestaande herinneringen voordat je opnieuw traint",
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Laad alleen schema-informatie (geen domeinkennis of voorbeelden)",
    )
    args = parser.parse_args()

    print("🎓 FundPilot Agent Training Pipeline")
    print("=" * 50)
    print()

    asyncio.run(train_agent(clear=args.clear, schema_only=args.schema_only))


if __name__ == "__main__":
    main()
