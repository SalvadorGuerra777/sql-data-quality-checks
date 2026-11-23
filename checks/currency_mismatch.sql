SELECT t.id, t.currency AS transaction_currency, a.currency AS account_currency
FROM transactions t
JOIN accounts a ON a.id = t.account_id
WHERE t.currency <> a.currency;
