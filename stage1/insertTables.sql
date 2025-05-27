-- Table Account
INSERT INTO Account VALUES (1, 'Compte Courant',   'Courant', 1500.00);
INSERT INTO Account VALUES (2, 'Épargne A',        'Épargne', 8000.50);
INSERT INTO Account VALUES (3, 'Professionnel',    'Pro',     25000.00);

-- Table TransactionType
INSERT INTO TransactionType VALUES (1, 'Dépôt',       'Dépot en espèces',       '0.00%', 'N');
INSERT INTO TransactionType VALUES (2, 'Retrait',     'Retrait distributeur',   '2.00%', 'N');
INSERT INTO TransactionType VALUES (3, 'Virement',    'Virement national',      '1.00%', 'Y');

-- Table Employee
INSERT INTO Employee VALUES (1, 'Alice', 'Dupont',   'Back Office');
INSERT INTO Employee VALUES (2, 'Marc',  'Leroy',    'Audit');
INSERT INTO Employee VALUES (3, 'Sara',  'Benali',   'IT');

-- Table Transaction
INSERT INTO "Transaction" VALUES (1001, 1,  1, DATE '2025-01-10', 200.00, 'Salaire',      'COMPLETED');
INSERT INTO "Transaction" VALUES (1002, 2,  2, DATE '2025-01-12', -50.00, 'Retrait ATM',   'COMPLETED');
INSERT INTO "Transaction" VALUES (1003, 3,  3, DATE '2025-01-15', -500.00,'Virement',     'PENDING');

-- Table Transfer
INSERT INTO Transfer VALUES (501, 1003, 3, 1, 'TRF-20250115', DATE '2025-01-15');
INSERT INTO Transfer VALUES (502, 1001, 1, 2, 'TRF-20250110', DATE '2025-01-10');
INSERT INTO Transfer VALUES (503, 1002, 2, 3, 'TRF-20250112', DATE '2025-01-12');

-- Table Check
INSERT INTO "Check" VALUES (301, 1001, 'CHK0001', 'Dupont SARL', DATE '2025-01-10', DATE '2025-01-12');
INSERT INTO "Check" VALUES (302, 1002, 'CHK0002', 'Leroy SA',   DATE '2025-01-12', NULL);
INSERT INTO "Check" VALUES (303, 1003, 'CHK0003', 'Benali SAS', DATE '2025-01-15', NULL);

-- Table TransactionFee
INSERT INTO TransactionFee VALUES (801, 1002, 'ATM Fee',  2.50, 'Frais distributeur', 'N');
INSERT INTO TransactionFee VALUES (802, 1003, 'Wire Fee', 5.00, 'Frais virement',     'Y');
INSERT INTO TransactionFee VALUES (803, 1001, 'None',     0.00, 'Pas de frais',       'N');

-- Table TransactionAudit
INSERT INTO TransactionAudit VALUES (901, 1003, DATE '2025-01-16', 'status', 'PENDING', 'COMPLETED', 2);
INSERT INTO TransactionAudit VALUES (902, 1002, DATE '2025-01-13', 'amount', ' -50.00', '-60.00',   1);
INSERT INTO TransactionAudit VALUES (903, 1001, DATE '2025-01-11', 'description', 'Salaire', 'Salaire net', 3);
