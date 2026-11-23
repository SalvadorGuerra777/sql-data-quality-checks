SELECT id, amount_cents
FROM transactions
WHERE amount_cents IS NULL
   OR typeof(amount_cents) <> 'integer'
   OR amount_cents = 0;
