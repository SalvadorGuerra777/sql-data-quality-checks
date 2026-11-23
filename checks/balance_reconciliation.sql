SELECT b.account_id,
       b.balance_cents AS reported,
       a.opening_balance_cents + COALESCE(SUM(t.amount_cents), 0) AS expected
FROM daily_balances b
JOIN accounts a ON a.id = b.account_id
LEFT JOIN transactions t ON t.account_id = b.account_id AND t.posted_on <= b.as_of
WHERE b.as_of = :as_of
GROUP BY b.account_id, b.balance_cents, a.opening_balance_cents
HAVING reported <> expected;
