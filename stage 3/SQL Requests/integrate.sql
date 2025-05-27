-- Integrate.sql – Intégration du module Account dans le projet Transaction
-- Ce script ajoute les tables Account et configure les clés étrangères, version corrigée PostgreSQL

BEGIN;

-- ===============================
-- 1. Table AccountType
-- ===============================
CREATE TABLE IF NOT EXISTS AccountType (
    type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(20) UNIQUE NOT NULL,
    description VARCHAR(100),
    interest_rate DECIMAL(5,2),
    min_balance DECIMAL(12,2),
    monthly_fee DECIMAL(8,2)
);

-- ===============================
-- 2. Table Account
-- ===============================
CREATE TABLE IF NOT EXISTS Account (
    account_id SERIAL PRIMARY KEY,
    customer_id VARCHAR(20),
    account_num VARCHAR(30) UNIQUE,
    opening_date DATE,
    current_balan NUMERIC(14,2),
    status VARCHAR(10),
    account_type VARCHAR(20),
    FOREIGN KEY (account_type) REFERENCES AccountType(type_name)
);

-- ===============================
-- 3. Table AccountActivity
-- ===============================
CREATE TABLE IF NOT EXISTS AccountActivity (
    activity_id SERIAL PRIMARY KEY,
    account_id INT REFERENCES Account(account_id),
    activity_type VARCHAR(20) CHECK (activity_type IN ('withdrawal','deposit','payment','refund','transfer')),
    activity_date DATE,
    amount DECIMAL(14,2),
    description TEXT
);

-- ===============================
-- 4. Table AccountStatement
-- ===============================
CREATE TABLE IF NOT EXISTS AccountStatement (
    statement_id SERIAL PRIMARY KEY,
    account_id INT REFERENCES Account(account_id),
    statement_period DATERANGE,
    generation_date DATE,
    opening_balance DECIMAL(14,2),
    closing_balance DECIMAL(14,2),
    file_reference TEXT
);

-- ===============================
-- 5. Table AccountRestriction
-- ===============================
CREATE TABLE IF NOT EXISTS AccountRestriction (
    restriction_id SERIAL,
    account_id INT REFERENCES Account(account_id),
    restriction_type VARCHAR(10) CHECK (restriction_type IN ('Full','Partial','None')),
    start_date DATE NOT NULL,
    end_date DATE CHECK (end_date > start_date),
    reason TEXT,
    PRIMARY KEY (restriction_id, account_id)
);

-- ===============================
-- 6. Table jointaccount
-- ===============================
CREATE TABLE IF NOT EXISTS jointaccount (
    joint_id SERIAL PRIMARY KEY,
    account_id INT REFERENCES Account(account_id),
    customer_id VARCHAR(20) NOT NULL,
    relationship_t VARCHAR(30),
    authorization_ VARCHAR(15)
);



COMMIT;


DO $$
BEGIN
    BEGIN
        ALTER TABLE "Transaction"
            ADD CONSTRAINT fk_transaction_account
            FOREIGN KEY ("account_id_FK") REFERENCES Account(account_id);
    EXCEPTION
        WHEN duplicate_object THEN
            -- La contrainte existe déjà, on ignore l'erreur
            NULL;
    END;
END $$;





-- FK sur Transfer.from_account_id_FK
DO $$
BEGIN
    BEGIN
        ALTER TABLE Transfer
            ADD CONSTRAINT fk_transfer_from_account
            FOREIGN KEY (from_account_id_FK) REFERENCES Account(account_id);
    EXCEPTION
        WHEN duplicate_object THEN
            -- La contrainte existe déjà, on ignore l'erreur
            NULL;
    END;
END $$;

-- FK sur Transfer.to_account_id_FK
DO $$
BEGIN
    BEGIN
        ALTER TABLE Transfer
            ADD CONSTRAINT fk_transfer_to_account
            FOREIGN KEY (to_account_id_FK) REFERENCES Account(account_id);
    EXCEPTION
        WHEN duplicate_object THEN
            -- La contrainte existe déjà, on ignore l'erreur
            NULL;
    END;
END $$;