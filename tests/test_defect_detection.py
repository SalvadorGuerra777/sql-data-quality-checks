"""Each check must flag exactly the row that breaks its rule."""
import pytest

import dq

DEFECTS = {
    "duplicate_transactions":
        "INSERT INTO transactions VALUES ('T0001', '1001', -12500, 'USD', '2026-10-01')",
    "orphan_transactions":
        "INSERT INTO transactions VALUES ('T9001', '9999', 1000, 'USD', '2026-10-05')",
    "invalid_amounts":
        "UPDATE transactions SET amount_cents = NULL WHERE id = 'T0005'",
    "currency_mismatch":
        "UPDATE transactions SET currency = 'EUR' WHERE id = 'T0004'",
    "future_dated_transactions":
        "UPDATE transactions SET posted_on = '2026-11-01' WHERE id = 'T0011'",
    "transactions_after_account_closed":
        "INSERT INTO transactions VALUES ('T9002', '1003', 500, 'USD', '2026-09-05')",
    "balance_reconciliation":
        "UPDATE daily_balances SET balance_cents = balance_cents + 1 WHERE account_id = '1001'",
    "missing_daily_balances":
        "DELETE FROM daily_balances WHERE account_id = '1004'",
}


def test_every_check_has_a_defect_case():
    assert sorted(DEFECTS) == dq.check_names()


@pytest.mark.parametrize("check", sorted(DEFECTS))
def test_check_detects_defect(db, check):
    db.execute(DEFECTS[check])
    assert len(dq.run_check(db, check)) == 1


@pytest.mark.parametrize("bad_amount", ["12.50", "abc", 0])
def test_non_integer_or_zero_amounts_are_flagged(db, bad_amount):
    db.execute("UPDATE transactions SET amount_cents = ? WHERE id = 'T0005'", (bad_amount,))
    assert [row[0] for row in dq.run_check(db, "invalid_amounts")] == ["T0005"]


def test_transaction_on_closing_day_is_allowed(db):
    db.execute("INSERT INTO transactions VALUES ('T9003', '1003', 100, 'USD', '2026-08-31')")
    assert dq.run_check(db, "transactions_after_account_closed") == []


def test_transaction_on_report_date_is_not_future_dated(db):
    db.execute("UPDATE transactions SET posted_on = ? WHERE id = 'T0011'", (dq.AS_OF,))
    assert dq.run_check(db, "future_dated_transactions") == []


def test_closed_account_does_not_need_a_daily_balance(db):
    db.execute("DELETE FROM daily_balances WHERE account_id = '1003'")
    assert dq.run_check(db, "missing_daily_balances") == []


def test_reconciliation_reports_expected_and_reported_values(db):
    db.execute("UPDATE daily_balances SET balance_cents = 0 WHERE account_id = '1004'")
    (row,) = dq.run_check(db, "balance_reconciliation")
    assert tuple(row) == ("1004", 0, 89999)
