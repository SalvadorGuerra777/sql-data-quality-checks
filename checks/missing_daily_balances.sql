SELECT a.id
FROM accounts a
WHERE a.status = 'ACTIVE'
  AND NOT EXISTS (
      SELECT 1 FROM daily_balances b
      WHERE b.account_id = a.id AND b.as_of = :as_of
  );
