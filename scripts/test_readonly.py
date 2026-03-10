"""Quick test for ReadOnlySqlRunner validation logic."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fundpilot_sql_runner import ReadOnlySqlRunner
from unittest.mock import MagicMock

mock_runner = MagicMock()
runner = ReadOnlySqlRunner(inner=mock_runner, max_rows=1000)

print("Testing read-only validation...")

blocked = [
    "INSERT INTO table VALUES (1)",
    "UPDATE table SET col = 1",
    "DELETE FROM table",
    "DROP TABLE test",
    "EXEC sp_help",
    "CREATE TABLE test (id int)",
    "TRUNCATE TABLE test",
    "ALTER TABLE test ADD col int",
]

for sql in blocked:
    try:
        runner._validate_read_only(sql)
        print(f"  FAIL Should have blocked: {sql}")
    except ValueError:
        print(f"  OK Blocked: {sql[:40]}")

allowed = [
    "SELECT * FROM [CWESystemData].[dbo].[Test]",
    "SELECT TOP 100 col1, col2 FROM [CWEProjectData].[dbo].[Donors]",
    "WITH cte AS (SELECT * FROM [CWESystemData].[dbo].[Calls]) SELECT * FROM cte",
    "SELECT COUNT(*) FROM [CWESystemConfig].[dbo].[Users]",
]

for sql in allowed:
    try:
        runner._validate_read_only(sql)
        print(f"  OK Allowed: {sql[:50]}")
    except ValueError as e:
        print(f"  FAIL Should have allowed: {sql[:50]} -> {e}")

print("\nDone!")
