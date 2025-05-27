
# 📦 Database Project – Stage 3: Integration and Views

This document summarizes the work done during Stage G, which focused on integrating two departmental database schemas and designing meaningful SQL views.

---

## 📌 Overview

- **Main project:** Transaction Management System
- **Integrated module:** Account Management System
- **Tools used:** PostgreSQL, pgAdmin, ERDPlus

---

## 🔗 Integration Process

1. Restored the external backup containing the Account module.
2. Reconstructed its **DSD** and generated a matching **ERD**.
3. Merged both ERDs into a unified **Integrated ERD**.
4. Created all missing tables in our main database (Transaction).
5. Added relevant FOREIGN KEY constraints between modules.
6. Populated tables with representative test data.

---

## 📸 Diagrams and Screenshots

### 📂 1. DSD of the integrated module (Account)
![Account ERD].(stage%203/Pictures/ACCNT_ERD.png)

### 📂 2. ERD of the integrated module
![ERD Diagram](Stage3/Pictures/ACCNT_ERD.png)

### 📂 3. Unified ERD after integration
👉 _Insert screenshot here: `Integrated_ERD.png`_

### 📂 4. Final DSD after integration
👉 _Insert screenshot here: `Unified_DSD.png`_

---

## 🧱 SQL Integration Script

- File: `Integrate.sql`
- Description: Contains all `CREATE TABLE` and `ALTER TABLE` statements to integrate the modules, without deleting existing data.

---

## 👁️ SQL Views

- File: `Views.sql`
- Description: Contains two views with JOINs, and two meaningful queries per view

### 👀 View 1: `TransactionOverviewView`

Displays transactions with type, status, and associated account:

```sql
SELECT * FROM TransactionOverviewView LIMIT 10;
```

👉 _Insert screenshot of result: `TransactionOverviewView.png`_

#### Query 1 – Transactions of type 'withdrawal'
```sql
SELECT * FROM TransactionOverviewView WHERE type_name = 'withdrawal';
```
👉 _Insert screenshot: `View_Query1.png`_

#### Query 2 – Average amount per type
```sql
SELECT type_name, AVG(amount) FROM TransactionOverviewView GROUP BY type_name;
```
👉 _Insert screenshot: `View_Query2.png`_

---

### 👀 View 2: `AccountSummaryView`

Displays account activities joined with account info:

```sql
SELECT * FROM AccountSummaryView LIMIT 10;
```

👉 _Insert screenshot: `AccountSummaryView.png`_

#### Query 1 – Activities with amount > 1000
```sql
SELECT * FROM AccountSummaryView WHERE amount > 1000;
```
👉 _Insert screenshot: `View_Query3.png`_

#### Query 2 – Activity count per type
```sql
SELECT activity_type, COUNT(*) FROM AccountSummaryView GROUP BY activity_type;
```
👉 _Insert screenshot: `View_Query4.png`_

---

## 📤 Files to Submit (Git)

- `Integrate.sql`
- `Views.sql`
- `backup3.backup`
- `README.md`
- All diagram and view result screenshots listed above

---

## 📌 Notes

- The integration was performed **without dropping existing tables** to preserve data integrity.
- All constraints were added with `ALTER TABLE`.
- Views were created to support future reporting or GUI display.
