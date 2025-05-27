
-- Integrate.sql : corrected unified schema and constraints
-- Generated on 2025-05-21

BEGIN;

-----------------------------------------------------------------
-- 1. AccountType
-----------------------------------------------------------------
DROP TABLE IF EXISTS AccountType CASCADE;

CREATE TABLE AccountType (
    type_id       SERIAL PRIMARY KEY,
    type_name     VARCHAR(20) UNIQUE NOT NULL,
    description   VARCHAR(100),
    interest_rate DECIMAL(5,2),
    min_balance   DECIMAL(12,2),
    monthly_fee   DECIMAL(8,2)
);



-----------------------------------------------------------------
-- 2. Account
-----------------------------------------------------------------
DROP TABLE IF EXISTS Account CASCADE;

CREATE TABLE Account (
    account_id      SERIAL PRIMARY KEY,
    customer_id     VARCHAR(20) NOT NULL,
    account_type    VARCHAR(20) NOT NULL REFERENCES AccountType(type_name),
    account_number  VARCHAR(30) UNIQUE NOT NULL,
    opening_date    DATE,
    current_balance DECIMAL(14,2),
    status          VARCHAR(10) CHECK (status IN ('active','pending','closed','dormant','suspended'))
);

-----------------------------------------------------------------
-- 3. AccountActivity
-----------------------------------------------------------------
DROP TABLE IF EXISTS AccountActivity CASCADE;

CREATE TABLE AccountActivity (
    activity_id   SERIAL PRIMARY KEY,
    account_id INT  REFERENCES Account(account_id),
    activity_type VARCHAR(20) CHECK (activity_type IN ('withdrawal','deposit','payment','refund','transfer')),
    activity_date DATE,
    amount        DECIMAL(14,2),
    description   TEXT
);

-----------------------------------------------------------------
-- 4. AccountStatement
-----------------------------------------------------------------
DROP TABLE IF EXISTS AccountStatement CASCADE;

CREATE TABLE AccountStatement (
    statement_id    SERIAL PRIMARY KEY,
    account_id     INT REFERENCES Account(account_id),
    statement_period DATERANGE,
    generation_date DATE,
    opening_balance DECIMAL(14,2),
    closing_balance DECIMAL(14,2),
    file_reference  TEXT
);

-----------------------------------------------------------------
-- 5. AccountRestriction
-----------------------------------------------------------------
DROP TABLE IF EXISTS AccountRestriction CASCADE;

CREATE TABLE AccountRestriction (
    restriction_id   SERIAL,
    account_id INT  REFERENCES Account(account_id),
    restriction_type VARCHAR(10) CHECK (restriction_type IN ('Full','Partial','None')),
    start_date       DATE NOT NULL,
    end_date         DATE CHECK (end_date > start_date),
    reason           TEXT,
    PRIMARY KEY (restriction_id, account_number)
);

-----------------------------------------------------------------
-- 6. joint_account
-----------------------------------------------------------------
DROP TABLE IF EXISTS joint_account CASCADE;

CREATE TABLE joint_account (
    joint_id           SERIAL PRIMARY KEY,
    account_id INT  REFERENCES Account(account_id),
    customer_id        VARCHAR(20) NOT NULL,
    relationship_type           VARCHAR(30) NOT NULL,
    authorization_level VARCHAR(15) CHECK (authorization_level IN ('read-only','limited','admin'))
);

COMMIT;
