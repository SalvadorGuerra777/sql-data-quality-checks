SELECT id, COUNT(*) AS copies
FROM transactions
GROUP BY id
HAVING COUNT(*) > 1;
