import pytest

import dq


@pytest.mark.parametrize("check", dq.check_names())
def test_clean_extract_passes(db, check):
    assert dq.run_check(db, check) == []


def test_extract_was_fully_loaded(db):
    counts = {table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in dq.TABLES}
    assert counts == {"accounts": 5, "transactions": 12, "daily_balances": 5}
