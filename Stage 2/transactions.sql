
-- ========================
-- 🔄 DEMONSTRATION ROLLBACK
-- ========================
BEGIN;

-- Étape 1 : Mise à jour temporaire
UPDATE "Transaction"
SET status = 'archived'
WHERE transaction_date < '2025-03-01';

-- Étape 2 : Vérification intermédiaire
SELECT transaction_id, status, transaction_date
FROM "Transaction"
WHERE transaction_date < '2025-03-01';

-- Étape 3 : Annulation
ROLLBACK;

-- Étape 4 : Vérification après annulation
SELECT transaction_id, status, transaction_date
FROM "Transaction"
WHERE transaction_date < '2025-03-01';

-- =======================
-- 💾 DEMONSTRATION COMMIT
-- =======================
BEGIN;

-- Étape 1 : Mise à jour réelle
UPDATE "TransactionFee"
SET waived = 'yes'
WHERE fee_type = 'ATM fee' AND amount > 5000000;

-- Étape 2 : Vérification intermédiaire
SELECT * FROM "TransactionFee"
WHERE fee_type = 'ATM fee' AND amount > 5000000;

-- Étape 3 : Validation
COMMIT;

-- Étape 4 : Vérification après validation
SELECT * FROM "TransactionFee"
WHERE fee_type = 'ATM fee' AND amount > 5000000;
