-- Table Transaction (mot réservé, on encadre entre guillemets)
CREATE TABLE "Transaction"
(
  transaction_id      INT            NOT NULL,
  account_id_FK       INT            NOT NULL,  -- FK vers Account(account_id)
  transaction_type    INT            NOT NULL,  -- FK vers TransactionType(type_id)
  transaction_date    DATE           NOT NULL,
  amount              NUMERIC(12,2)  NOT NULL,
  description         VARCHAR2(255)  NULL,
  status              VARCHAR2(50)   NULL,
  PRIMARY KEY (transaction_id)
);

-- Table TransactionType
CREATE TABLE TransactionType
(
  type_id            INT           NOT NULL,
  type_name          VARCHAR2(50)  NOT NULL,
  description        VARCHAR2(255) NULL,
  fee_structure      VARCHAR2(100) NULL,
  requires_approval  CHAR(1)       NOT NULL,  -- 'Y' ou 'N'
  PRIMARY KEY (type_id)
);

-- Table Transfer
CREATE TABLE Transfer
(
  transfer_id           INT            NOT NULL,
  transaction_id        INT            NOT NULL,  -- FK vers "Transaction"(transaction_id)
  from_account_id_FK    INT            NOT NULL,  -- FK vers Account(account_id)
  to_account_id_FK      INT            NOT NULL,  -- FK vers Account(account_id)
  transfer_reference    VARCHAR2(100)  NULL,
  transfer_date         DATE           NOT NULL,
  PRIMARY KEY (transfer_id),
  FOREIGN KEY (transaction_id) REFERENCES "Transaction"(transaction_id)
);

-- Table Check (mot réservé, on encadre entre guillemets)
CREATE TABLE "Check"
(
  check_id       INT           NOT NULL,
  transaction_id INT           NOT NULL,  -- FK vers "Transaction"(transaction_id)
  check_number   VARCHAR2(50)  NULL,
  payee_name     VARCHAR2(100) NULL,
  issue_date     DATE          NOT NULL,
  clearance_date DATE          NULL,
  PRIMARY KEY (check_id),
  FOREIGN KEY (transaction_id) REFERENCES "Transaction"(transaction_id)
);

-- Table TransactionFee
CREATE TABLE TransactionFee
(
  fee_id         INT            NOT NULL,
  transaction_id INT            NOT NULL,  -- FK vers "Transaction"(transaction_id)
  fee_type       VARCHAR2(50)   NOT NULL,
  amount         NUMERIC(10,2)  NOT NULL,
  description    VARCHAR2(255)  NULL,
  waived         CHAR(1)        NOT NULL,  -- 'Y' ou 'N'
  PRIMARY KEY (fee_id),
  FOREIGN KEY (transaction_id) REFERENCES "Transaction"(transaction_id)
);

-- Table TransactionAudit
CREATE TABLE TransactionAudit
(
  audit_id        INT           NOT NULL,
  transaction_id  INT           NOT NULL,  -- FK vers "Transaction"(transaction_id)
  audit_timestamp DATE          NOT NULL,
  changed_field   VARCHAR2(100) NOT NULL,
  old_value       VARCHAR2(255) NULL,
  new_value       VARCHAR2(255) NULL,
  employee_id_FK  INT           NOT NULL,  -- FK vers Employee(employee_id)
  PRIMARY KEY (audit_id),
  FOREIGN KEY (transaction_id) REFERENCES "Transaction"(transaction_id)
);
