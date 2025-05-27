
-- Views.sql – Vues pour le projet intégré (Transaction + Account)

-- ============================================================
-- 🔍 Vue 1 : TransactionOverviewView
-- Description : Vue combinant les transactions avec leur type et le compte associé
-- ============================================================
CREATE OR REPLACE VIEW TransactionOverviewView AS
SELECT 
    t.transaction_id,
    t.transaction_date,
    t.amount,
    t.status,
    tt.type_name,
    a.account_num,
    a.customer_id
FROM "Transaction" t
JOIN "transaction_type" tt ON t.transaction_type = tt.type_id
JOIN Account a ON t."account_id_FK" = a.account_id;
-- ============================================================
-- 🔍 Vue 2 : AccountSummaryView
-- Description : Vue listant les comptes avec leurs activités bancaires
-- ============================================================
CREATE OR REPLACE VIEW AccountSummaryView AS
SELECT 
    a.account_id,
    a.account_num,
    a.customer_id,
    a.status,
    ac.activity_type,
    ac.activity_date,
    ac.amount
FROM Account a
JOIN AccountActivity ac ON a.account_id = ac.account_id;

-- ============================================================
-- ✅ Requêtes sur TransactionOverviewView
-- ============================================================

-- 1. Transactions de type "withdrawal"
SELECT * 
FROM TransactionOverviewView
WHERE type_name = 'withdrawal';

-- 2. Moyenne des montants par type de transaction
SELECT type_name, AVG(amount) AS avg_amount
FROM TransactionOverviewView
GROUP BY type_name;

-- ============================================================
-- ✅ Requêtes sur AccountSummaryView
-- ============================================================

-- 1. Activités dont le montant est supérieur à 1000
SELECT * 
FROM AccountSummaryView
WHERE amount > 1000;

-- 2. Nombre d’activités par type
SELECT activity_type, COUNT(*) AS total
FROM AccountSummaryView
GROUP BY activity_type;
