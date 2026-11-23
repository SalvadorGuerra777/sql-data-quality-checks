SELECT t.id, t.posted_on, a.closed_on
FROM transactions t
JOIN accounts a ON a.id = t.account_id
WHERE a.status = 'CLOSED'
  AND t.posted_on > a.closed_on;
