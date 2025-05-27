import psycopg2
import pandas as pd
from pathlib import Path
from psycopg2 import sql

# 1. Charger les données Excel
excel_path = Path.home() / 'PycharmProjects' / 'import_audit' / 'transaction_audit_randomized.xlsx'
df = pd.read_excel(excel_path)

# Si audit_timestamp est en format string, on le convertit en date Python
df['audit_timestamp'] = pd.to_datetime(df['audit_timestamp']).dt.date

# 2. Connexion à PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="mydatabase",
    user="ruben",        # ou le nom exact de votre rôle PostgreSQL
    password="2810"
)
cur = conn.cursor()

# 3. (Optionnel) Création automatique de la table si elle n'existe pas
cur.execute("""
CREATE TABLE IF NOT EXISTS transaction_audit (
    audit_id          INTEGER     PRIMARY KEY DEFAULT nextval('transaction_audit_audit_id_seq'),
    transaction_id    INTEGER     NOT NULL,
    audit_timestamp   DATE        NOT NULL,
    changed_field     VARCHAR(100) NOT NULL,
    old_value         VARCHAR(255),
    new_value         VARCHAR(255),
    employee_id_FK    VARCHAR(255) NOT NULL
);
""")
conn.commit()

# 4. Préparer la requête INSERT (on laisse PostgreSQL gérer audit_id)
insert_query = sql.SQL("""
    INSERT INTO transaction_audit (
        transaction_id,
        audit_timestamp,
        changed_field,
        old_value,
        new_value,
        "employee_id_FK"
    )
    VALUES (%s, %s, %s, %s, %s, %s)
""")

# 5. Itérer sur le DataFrame et insérer
for _, row in df.iterrows():
    cur.execute(
        insert_query,
        (
            int(row['transaction_id']),
            row['audit_timestamp'],
            row['changed_field'],
            row['old_value'],
            row['new_value'],
            row['employee_id_FK']
        )
    )

# 6. Valider et fermer
conn.commit()
cur.close()
conn.close()

print("Import terminé ✔️")
