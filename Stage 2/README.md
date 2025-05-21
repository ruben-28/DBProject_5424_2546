
# 📊 Database Project – Stage 2: Queries and Constraints

This document details the objectives, deliverables, and structure of stage 2 of the database project. This phase is centered around advanced SQL usage, data integrity via constraints, and safe transactional control.

---

## 🎯 Stage 2 Goals

The aim of this phase is to demonstrate your ability to:

1. **Formulate complex SQL queries** that provide meaningful insights from multiple tables.
2. **Manipulate and clean data** using `DELETE` and `UPDATE` statements based on real business logic.
3. **Ensure data consistency** through explicit SQL constraints.
4. **Safely manage database changes** using PostgreSQL transaction commands (`ROLLBACK`, `COMMIT`).

---

## 📁 Deliverables and File Descriptions

### ✅ `queries.sql`

This file contains:

* **8 non-trivial `SELECT` queries** using:
  * Multi-table joins (`JOIN`)
  * Date manipulation (`TO_CHAR`)
  * Aggregation (`SUM`, `AVG`, `COUNT`)
  * Subqueries and filters
* Each query returns **more than 2 columns** and provides insights that would be useful for GUI display (e.g. transaction details, user-friendly names, monthly summaries).
* **3 `DELETE` queries**, carefully designed to:
  * Remove waived fees under specific conditions
  * Clean old or orphaned data (e.g. transfers without valid transactions)
* **3 `UPDATE` queries** to:
  * Automatically set default descriptions where missing
  * Archive or finalize old transactions
  * Modify large fees to simulate dynamic policy changes

> ✅ Queries use double quotes for table and column names to respect PostgreSQL case sensitivity (e.g. `"Transaction"` vs `transaction`).

---

### ✅ `constraints.sql`

This script applies **3 key constraints** to improve data quality and enforce business rules:

* `NOT NULL` on `"Transaction"."status"` to ensure every transaction has a defined state.
* `CHECK (amount > 0)` on `"TransactionFee"."amount"` to avoid negative or zero-value fees.
* `DEFAULT 'no'` on `"TransactionFee"."waived"` to ensure fees are not waived unless explicitly defined.

> These constraints simulate real-world enforcement rules within a banking or transaction system.

---

### ✅ `transactions.sql`

This file demonstrates **manual control of transactions** using:

#### 🔁 **ROLLBACK Transaction**
* Starts a transaction with `BEGIN`
* Applies a temporary update (e.g., archiving old transactions)
* Rolls back the change with `ROLLBACK`
* Verifies that the original values are restored

#### 💾 **COMMIT Transaction**
* Starts a transaction
* Updates records (e.g., setting fees to waived for high-value ATM charges)
* Saves the changes using `COMMIT`
* Confirms that the changes are now permanent

> These scenarios reflect **safe update procedures**, which are essential in production environments to avoid data corruption.


---

## 🔍 Expected Results & Testing Tips

* **SELECT queries** should return user-friendly, readable information (e.g., type names, amounts, formatted dates).
* **DELETE and UPDATE queries** should show row modifications when you run `SELECT COUNT(*)` before and after.
* **ROLLBACK** must undo all changes in a transaction.
* **COMMIT** should make updates persistent even after reconnecting to the DB.
* **Constraints** should be tested by attempting to insert invalid data (e.g., a negative fee).

---

End of Stage 2
