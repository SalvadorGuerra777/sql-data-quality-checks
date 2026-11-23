"""Load the bank extracts into SQLite and run the data quality checks."""
import csv
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).parent
CHECKS_DIR = ROOT / "checks"
DATA_DIR = Path(os.getenv("DQ_DATA_DIR", ROOT / "data"))
AS_OF = os.getenv("DQ_AS_OF", "2026-10-31")
TABLES = ("accounts", "transactions", "daily_balances")


def connect(data_dir=DATA_DIR):
    conn = sqlite3.connect(":memory:")
    conn.executescript((ROOT / "schema.sql").read_text())
    for table in TABLES:
        with open(data_dir / f"{table}.csv", newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        columns = list(rows[0])
        placeholders = ", ".join("?" * len(columns))
        conn.executemany(
            f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
            [[row[c] or None for c in columns] for row in rows],
        )
    return conn


def check_names():
    return sorted(path.stem for path in CHECKS_DIR.glob("*.sql"))


def run_check(conn, name, as_of=AS_OF):
    sql = (CHECKS_DIR / f"{name}.sql").read_text()
    return conn.execute(sql, {"as_of": as_of}).fetchall()


def main():
    conn = connect()
    failed = 0
    print(f"Data quality report as of {AS_OF}\n")
    for name in check_names():
        violations = run_check(conn, name)
        failed += bool(violations)
        print(f"{'FAIL' if violations else 'PASS'}  {name:<36} {len(violations)} row(s)")
        for row in violations:
            print(f"      {row}")
    print(f"\n{len(check_names()) - failed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
