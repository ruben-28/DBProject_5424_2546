
-- Requête 1
SELECT
    tt.type_name AS transaction_type,
    TO_CHAR(t.transaction_date::DATE, 'YYYY-MM') AS year_month,
    SUM(t.amount) AS total_amount
FROM
    "Transaction" t
JOIN
    "Transfer" tr ON t.transaction_id = tr.transaction_id
JOIN
    "TransactionType" tt ON t.transaction_type = tt.type_id
GROUP BY
    tt.type_name,
    TO_CHAR(t.transaction_date::DATE, 'YYYY-MM')
ORDER BY
    year_month, total_amount DESC;

-- Requête 2
SELECT
    t.transaction_id,
    t.amount,
    tr.from_account_id_FK,
    tr.to_account_id_FK,
    t.transaction_date
FROM
    "Transaction" t
JOIN
    "Transfer" tr ON t.transaction_id = tr.transaction_id
WHERE
    t.amount > 1000000
ORDER BY
    t.amount DESC;

-- Requête 3
SELECT
    tf.fee_type,
    COUNT(*) AS count,
    AVG(tf.amount) AS average_fee
FROM
    "TransactionFee" tf
GROUP BY
    tf.fee_type
ORDER BY
    average_fee DESC;

-- Requête 4
SELECT
    employee_id_FK,
    COUNT(*) AS total_changes,
    MIN(audit_timestamp) AS first_change,
    MAX(audit_timestamp) AS last_change
FROM
    "transaction_audit"
GROUP BY
    employee_id_FK
ORDER BY
    total_changes DESC;

-- Requête 5
SELECT
    t.transaction_id,
    t.amount,
    tf.fee_type,
    tf.amount AS fee_amount,
    tf.waived
FROM
    "Transaction" t
JOIN
    "TransactionFee" tf ON t.transaction_id = tf.transaction_id
WHERE
    tf.waived = 'yes';

-- Requête 6
SELECT
    t.status,
    TO_CHAR(t.transaction_date::DATE, 'YYYY-MM') AS year_month,
    COUNT(*) AS transaction_count
FROM
    "Transaction" t
GROUP BY
    t.status, TO_CHAR(t.transaction_date::DATE, 'YYYY-MM')
ORDER BY
    transaction_count DESC;

-- Requête 7
SELECT
    ta.transaction_id,
    ta.changed_field,
    ta.old_value,
    ta.new_value,
    ta.audit_timestamp,
    t.amount,
    t.status
FROM
    "transaction_audit" ta
JOIN
    "Transaction" t ON ta.transaction_id = t.transaction_id
ORDER BY
    ta.audit_timestamp DESC;

-- Requête 8
SELECT
    transaction_id,
    amount,
    transaction_date
FROM
    "Transaction"
WHERE
    amount > (
        SELECT AVG(amount) FROM "Transaction"
    )
ORDER BY
    amount DESC;

-- DELETE 1
DELETE FROM "TransactionFee"
WHERE waived = 'yes'
  AND transaction_id IN (
    SELECT transaction_id
    FROM "Transaction"
    WHERE amount < 1000000000
);

-- DELETE 2
DELETE FROM "Transfer"
WHERE transaction_id IN (
    SELECT transaction_id
    FROM "Transaction"
    WHERE transaction_date < '2025-02-01'
);

-- DELETE 3
DELETE FROM "transaction_audit"
WHERE transaction_id NOT IN (
    SELECT transaction_id FROM "Transaction"
);

-- UPDATE 1
UPDATE "Transaction"
SET status = 'completed'
WHERE status = 'pending'
  AND transaction_date < CURRENT_DATE - INTERVAL '6 months';

-- UPDATE 2
UPDATE "TransactionFee"
SET amount = amount * 2
WHERE waived = 'no'
  AND transaction_id IN (
    SELECT transaction_id FROM "Transaction" WHERE amount > 1000000
);

-- UPDATE 3
UPDATE "Transaction"
SET desccription = 'No description provided'
WHERE desccription IS NULL OR desccription = '';
