SELECT id, posted_on
FROM transactions
WHERE posted_on > :as_of;
