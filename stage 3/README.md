
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
![Account DSD](stage%203/Pictures/DSD_Account.jpg)

### 📂 2. ERD of the integrated module
![Account ERD](stage%203/Pictures/ACCNT_ERD.png)

### 📂 3. Unified ERD after integration
![Integrated_ERD](stage%203/Pictures/MergedERD.png)

### 📂 4. Final DSD after integration
![Unified_DSD](stage%203/Pictures/mergedDSD.jpg)


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
SELECT * FROM TransactionOverviewView ;
```

![Transaction View](stage%203/Pictures/TransactionView.png)


#### Query 1 – Transactions of type 'withdrawal'
```sql
SELECT * FROM TransactionOverviewView WHERE type_name = 'purhase';
```
![View1_Query1](stage%203/Pictures/View1_Query1.png)

#### Query 2 – Average amount per type
```sql
SELECT type_name, AVG(amount) FROM TransactionOverviewView GROUP BY type_name;
```
![View1_Query2](stage%203/Pictures/View1_Query2.png)

---

### 👀 View 2: `AccountSummaryView`

Displays account activities joined with account info:

```sql
SELECT * FROM AccountSummaryView ;
```

![AccntSumView](stage%203/Pictures/AccntSumView.png)

#### Query 1 – Activities with amount > 1000
```sql
SELECT * FROM AccountSummaryView WHERE amount > 1000;
```
![AccntSumView_Query1](stage%203/Pictures/AccntSumView_Query1.png)

#### Query 2 – Activity count per type
```sql
SELECT activity_type, COUNT(*) FROM AccountSummaryView GROUP BY activity_type;
```
![AccntSumView_Query2](stage%203/Pictures/AccntSumView_Query2.png)

---

## 📤 Files to Submit (Git)

- `Integrate.sql`
- `Views.sql`
- `backup3.backup`
- `README.md`
- All diagram and view result screenshots listed above

---

end of stage 3
