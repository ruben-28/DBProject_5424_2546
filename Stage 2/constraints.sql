
-- NOT NULL constraint on the 'status' column in the "Transaction" table
ALTER TABLE "Transaction"
ALTER COLUMN status SET NOT NULL;

-- CHECK constraint on the 'amount' column in the "TransactionFee" table
ALTER TABLE "TransactionFee"
ADD CONSTRAINT chk_positive_fee_amount CHECK (amount > 0);

-- DEFAULT constraint on the 'waived' column in the "TransactionFee" table
ALTER TABLE "TransactionFee"
ALTER COLUMN waived SET DEFAULT 'no';
