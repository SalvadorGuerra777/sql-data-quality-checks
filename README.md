# sql-data-quality-checks

![Data quality](https://github.com/SalvadorGuerra777/sql-data-quality-checks/actions/workflows/data-quality.yml/badge.svg)

SQL data quality checks for a small banking dataset: accounts, transactions and the daily balances a reporting system publishes. Each rule is a plain SQL query that returns the rows breaking it, and a PyTest suite proves the rules pass on clean data and catch each kind of bad data.

The data is synthetic. It mirrors the kind of validation done when a core banking system feeds a reporting layer: nothing lost, nothing duplicated, and balances that reconcile to the cent.

## Tech stack

- SQL (SQLite, in memory)
- Python 3.12+ standard library (`sqlite3`, `csv`)
- PyTest
- GitHub Actions

## Project structure

```
├── schema.sql              # accounts, transactions, daily_balances
├── data/                   # CSV extracts (clean baseline)
├── checks/                 # One SQL rule per file; returns the violating rows
├── dq.py                   # Loads the CSVs and runs every check
├── tests/
│   ├── test_clean_data.py       # Every check passes on the clean extract
│   └── test_defect_detection.py # Every check flags the bad row injected for it
└── .github/workflows/data-quality.yml
```

## Checks

| Check | Rule |
|---|---|
| `duplicate_transactions` | A transaction id appears only once |
| `orphan_transactions` | Every transaction belongs to an existing account |
| `invalid_amounts` | Amounts are whole cents, not null and not zero |
| `currency_mismatch` | Transaction currency matches the account currency |
| `future_dated_transactions` | No transaction is posted after the report date |
| `transactions_after_account_closed` | Closed accounts have no activity after their closing date |
| `balance_reconciliation` | Reported balance = opening balance + transactions up to the report date |
| `missing_daily_balances` | Every active account has a balance for the report date |

Amounts are stored as integer cents to avoid floating-point rounding errors in money calculations.

## Setup

```bash
git clone https://github.com/SalvadorGuerra777/sql-data-quality-checks.git
cd sql-data-quality-checks
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running

Data quality report:

```bash
python dq.py
```

```
Data quality report as of 2026-10-31

PASS  balance_reconciliation               0 row(s)
PASS  currency_mismatch                    0 row(s)
PASS  duplicate_transactions               0 row(s)
PASS  future_dated_transactions            0 row(s)
PASS  invalid_amounts                      0 row(s)
PASS  missing_daily_balances               0 row(s)
PASS  orphan_transactions                  0 row(s)
PASS  transactions_after_account_closed    0 row(s)

8 passed, 0 failed
```

The script exits with code 1 if any check fails, so it can gate a pipeline. To validate another extract, point it at a folder with the same three CSV files:

| Variable | Default | Description |
|---|---|---|
| `DQ_DATA_DIR` | `data/` | Folder with `accounts.csv`, `transactions.csv`, `daily_balances.csv` |
| `DQ_AS_OF` | `2026-10-31` | Report date used by the date-based checks |

Tests:

```bash
pytest
```

## What the tests verify

- All 8 checks return no rows on the clean extract, and all rows were loaded.
- Each check flags exactly one row when one defect of its type is injected (duplicate, orphan, null amount, wrong currency, future date, activity after closing, off-by-one-cent balance, missing balance). A test also fails if a new check is added without a defect case.
- Boundary cases: a transaction on the closing day or on the report date is valid, a closed account doesn't need a daily balance, and amounts like `12.50`, `abc` or `0` are rejected.
- The reconciliation check reports both the reported and the expected balance, so the difference can be investigated.

Last local run: `25 passed`.
