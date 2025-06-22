
-- ====================================
-- Trigger Function : log_transaction_update
-- ====================================

CREATE OR REPLACE FUNCTION log_transaction_update()
RETURNS TRIGGER AS $$
DECLARE
    field TEXT;
    old_val TEXT;
    new_val TEXT;
BEGIN
    IF NEW."amount" IS DISTINCT FROM OLD."amount" THEN
        field := 'amount';
        old_val := OLD."amount"::TEXT;
        new_val := NEW."amount"::TEXT;
    ELSIF NEW."status" IS DISTINCT FROM OLD."status" THEN
        field := 'status';
        old_val := OLD."status";
        new_val := NEW."status";
    ELSIF NEW."description" IS DISTINCT FROM OLD."description" THEN
        field := 'description';
        old_val := OLD."description";
        new_val := NEW."description";
    ELSE
        RETURN NEW;
    END IF;

    INSERT INTO "transaction_audit" (
        "transaction_id",
        "audit_timestamp",
        "changed_field",
        "old_value",
        "new_value",
        "employee_id_FK"
    ) VALUES (
        NEW."transaction_id",
        CURRENT_TIMESTAMP,
        field,
        old_val,
        new_val,
        NULL
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_log_transaction_update
AFTER UPDATE ON "Transaction"
FOR EACH ROW
EXECUTE FUNCTION log_transaction_update();

-- ====================================
-- Trigger Function : update_account_balance_after_activity
-- ====================================

CREATE OR REPLACE FUNCTION update_account_balance_after_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE "account"
    SET "current_balan" = "current_balan" + NEW."amount"
    WHERE "account_id" = NEW."account_id";

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_account_balance
AFTER INSERT ON "accountactivity"
FOR EACH ROW
EXECUTE FUNCTION update_account_balance_after_activity();
