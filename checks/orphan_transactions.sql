SELECT t.id, t.account_id
FROM transactions t
LEFT JOIN accounts a ON a.id = t.account_id
WHERE a.id IS NULL;
