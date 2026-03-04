"""Discover common column patterns across project tables."""
import pyodbc, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

conn_str = os.getenv("MSSQL_CONN_STR")
conn = pyodbc.connect(conn_str, timeout=15)
cursor = conn.cursor()

print("=== TOP 50 MEEST VOORKOMENDE KOLOMMEN IN CWEProjectData ===")
cursor.execute("""
    SELECT TOP 50 c.COLUMN_NAME, c.DATA_TYPE, COUNT(DISTINCT c.TABLE_NAME) as table_count
    FROM [CWEProjectData].INFORMATION_SCHEMA.COLUMNS c
    JOIN [CWEProjectData].INFORMATION_SCHEMA.TABLES t
        ON c.TABLE_NAME = t.TABLE_NAME AND c.TABLE_SCHEMA = t.TABLE_SCHEMA
    WHERE t.TABLE_TYPE = 'BASE TABLE'
    GROUP BY c.COLUMN_NAME, c.DATA_TYPE
    HAVING COUNT(DISTINCT c.TABLE_NAME) > 10
    ORDER BY COUNT(DISTINCT c.TABLE_NAME) DESC
""")
for row in cursor.fetchall():
    print(f"  {row[0]:35s} {row[1]:20s} in {row[2]} tabellen")

print()
print("=== KOLOMMEN VAN TYPISCHE PROJECT-TABEL (KLF2401) ===")
cursor.execute("""
    SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
    FROM [CWEProjectData].INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'KLF2401'
    ORDER BY ORDINAL_POSITION
""")
for row in cursor.fetchall():
    maxlen = f"({row[2]})" if row[2] else ""
    print(f"  {row[0]:35s} {row[1]}{maxlen}")

print()
print("=== KOLOMMEN VAN CWESystemConfig TABEL: Project ===")
for tbl in ["Project", "Projects", "Workgroup", "Workgroups", "ResultCode", "ResultCodes"]:
    cursor.execute("""
        SELECT TABLE_NAME FROM [CWESystemConfig].INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME = ? AND TABLE_TYPE = 'BASE TABLE'
    """, tbl)
    if cursor.fetchone():
        print(f"\n  Tabel gevonden: {tbl}")
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM [CWESystemConfig].INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = '{tbl}'
            ORDER BY ORDINAL_POSITION
        """)
        for r in cursor.fetchall():
            print(f"    {r[0]:35s} {r[1]}")

print()
print("=== KEY TABELLEN IN CWESystemData ===")
for tbl in ["CallHistory", "CallData", "AgentActivity", "WorkedHours", "ACD"]:
    cursor.execute("""
        SELECT TABLE_NAME FROM [CWESystemData].INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME LIKE ? AND TABLE_TYPE = 'BASE TABLE'
    """, f"%{tbl}%")
    matches = cursor.fetchall()
    for m in matches:
        print(f"  Gevonden: {m[0]}")

print()
print("=== TABEL NAMEN-PATROON IN CWEProjectData (eerste 30) ===")
cursor.execute("""
    SELECT TOP 30 TABLE_NAME
    FROM [CWEProjectData].INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE'
    ORDER BY TABLE_NAME
""")
for row in cursor.fetchall():
    print(f"  {row[0]}")

print()
print("=== TOTAAL TABELLEN PER DATABASE ===")
for db in ["CWESystemConfig","CWESystemData","CWEProjectData",
           "CWESystemConfig_Archive","CWESystemData_Archive","CWEProjectData_Archive"]:
    cursor.execute(f"SELECT COUNT(*) FROM [{db}].INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
    cnt = cursor.fetchone()[0]
    print(f"  {db:35s} {cnt} tabellen")

print()
print("=== TABELLEN MET CollectDate KOLOM (eerste 20) ===")
cursor.execute("""
    SELECT TOP 20 TABLE_NAME
    FROM [CWEProjectData].INFORMATION_SCHEMA.COLUMNS
    WHERE COLUMN_NAME = 'CollectDate'
    ORDER BY TABLE_NAME
""")
for row in cursor.fetchall():
    print(f"  {row[0]}")

print()
print("=== CWESystemConfig: ALLE TABELLEN ===")
cursor.execute("""
    SELECT TABLE_NAME FROM [CWESystemConfig].INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME
""")
for row in cursor.fetchall():
    print(f"  {row[0]}")

print()
print("=== CWESystemData: ALLE TABELLEN ===")
cursor.execute("""
    SELECT TABLE_NAME FROM [CWESystemData].INFORMATION_SCHEMA.TABLES
    WHERE TABLE_TYPE = 'BASE TABLE' ORDER BY TABLE_NAME
""")
for row in cursor.fetchall():
    print(f"  {row[0]}")

conn.close()
print("\nDone.")
