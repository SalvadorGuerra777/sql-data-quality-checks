CREATE TABLE accounts (
    id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    currency TEXT NOT NULL,
    status TEXT NOT NULL,
    opened_on TEXT NOT NULL,
    closed_on TEXT,
    opening_balance_cents INTEGER NOT NULL
);

-- Raw extracts from the core system and the reporting layer, loaded without
-- constraints on purpose: the checks are what catch bad data.
CREATE TABLE transactions (
    id TEXT,
    account_id TEXT,
    amount_cents INTEGER,
    currency TEXT,
    posted_on TEXT
);

CREATE TABLE daily_balances (
    account_id TEXT,
    as_of TEXT,
    balance_cents INTEGER
);
