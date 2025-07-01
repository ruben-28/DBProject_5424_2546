import streamlit as st
import pandas as pd
from sqlalchemy import text
from stage5 import (
    Transaction,
    Transfer,
    Check,
    Session,
    add_transaction,
    add_transfer,
    add_check,
    update_transaction,
    update_transfer,
    update_check,
    delete_transaction,
    delete_transfer,
    delete_check,
)

# --- AUTHENTIFICATION -------------------------------------------------------
USERS = {"admin": "admin"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("Connexion")
    u = st.text_input("Utilisateur")
    p = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if USERS.get(u) == p:
            st.session_state.logged_in = True

 main
        else:
            st.error("Identifiants invalides")
    st.stop()

# --- CONFIGURATION GÉNÉRALE ---
st.set_page_config(
    page_title="Tableau de Bord Transactions",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SIDEBAR ---
st.sidebar.image("https://placehold.co/200x80?text=Votre+Logo", use_column_width=True)
st.sidebar.title("Navigation")
page = st.sidebar.radio("", [
    "📊 Tableau de Bord",
    "🔧 Gestion CRUD",
    "📈 Rapports",
    "⚙️ Procédures"
])

# --- FONCTIONS UTILES ---
def fetch_data(model):
    with Session() as session:
        rows = session.query(model).all()
        # on retire l’attribut _sa_instance_state
        data = []
        for r in rows:
            d = r.__dict__.copy()
            d.pop("_sa_instance_state", None)
            data.append(d)
        return pd.DataFrame(data)

def get_monthly_totals_by_type():
    sql = """
    SELECT
      t.transaction_type    AS transaction_type,
      TO_CHAR(t.transaction_date::DATE, 'YYYY-MM') AS year_month,
      SUM(t.amount)        AS total_amount
    FROM "Transaction" t
    JOIN transfer tr ON t.transaction_id = tr.transaction_id
    GROUP BY
      t.transaction_type, year_month
    ORDER BY
      year_month, total_amount DESC;
    """
    with Session() as session:
        result = session.execute(text(sql)).fetchall()
    return pd.DataFrame(result, columns=["transaction_type", "year_month", "total_amount"])

def get_large_transactions(threshold=1_000_000):
    sql = """
    SELECT
      t.transaction_id,
      t.amount,
      tr.from_account_id_fk AS from_account,
      tr.to_account_id_fk   AS to_account,
      t.transaction_date
    FROM "Transaction" t
    JOIN transfer tr ON t.transaction_id = tr.transaction_id
    WHERE t.amount > :threshold
    ORDER BY t.amount DESC
    LIMIT 50;
    """
    with Session() as session:
        result = session.execute(text(sql), {"threshold": threshold}).fetchall()
    return pd.DataFrame(result, columns=[
        "transaction_id", "amount", "from_account", "to_account", "transaction_date"
    ])

def run_update_inactive_accounts():
    with Session() as session:
        session.execute(text("CALL update_inactive_accounts()"))
        session.commit()

def run_check_and_block(acc_id, threshold):
    with Session() as session:
        session.execute(
            text("CALL check_and_block_account_if_overdraft(:acc_id, :threshold)"),
            {"acc_id": acc_id, "threshold": threshold}
        )
        session.commit()

# --- PAGE: Tableau de Bord ---
if page == "📊 Tableau de Bord":
    st.title("📊 Tableau de Bord")
    # Comptages globaux
    with Session() as session:
        cnt_tx = session.query(Transaction).count()
        cnt_tr = session.query(Transfer).count()
        cnt_ch = session.query(Check).count()
    col1, col2, col3 = st.columns(3)
    col1.metric("Transactions", cnt_tx)
    col2.metric("Transferts",   cnt_tr)
    col3.metric("Chèques",       cnt_ch)

    st.markdown("---")
    st.subheader("5 dernières transactions")
    recent = (
        Session()
        .query(Transaction)
        .order_by(Transaction.transaction_date.desc())
        .limit(5)
        .all()
    )
    df_recent = pd.DataFrame([{
        "ID": r.transaction_id,
        "Date": r.transaction_date,
        "Montant": float(r.amount),
        "Statut": r.status
    } for r in recent])
    st.table(df_recent)

# --- PAGE: Gestion CRUD ---
elif page == "🔧 Gestion CRUD":
    st.title("🔧 Gestion CRUD")
    table = st.selectbox("Choisir la table à gérer", ["Transaction", "Transfer", "Check"])
    model = {"Transaction": Transaction, "Transfer": Transfer, "Check": Check}[table]

    left, right = st.columns((2, 1))
    with left:
        st.subheader(f"Liste des {table}s")
        df = fetch_data(model)
        st.dataframe(df, use_container_width=True)

    with right:
        st.subheader(f"Ajouter un nouveau {table}")
        with st.form(f"form_add_{table}", clear_on_submit=True):
            if table == "Transaction":
                a1 = st.number_input("Account ID", step=1, min_value=1)
                a2 = st.number_input("Type ID",    step=1, min_value=1)
                a3 = st.date_input("Date")
                a4 = st.number_input("Montant", format="%.2f")
                a5 = st.text_input("Description")
                a6 = st.text_input("Statut")
                if st.form_submit_button("Ajouter"):
                    add_transaction(a1, a2, a3, a4, a5, a6)
                    st.success("Transaction ajoutée")
            elif table == "Transfer":
                t1 = st.number_input("Transaction ID", step=1, min_value=1)
                t2 = st.number_input("From Account ID", step=1, min_value=1)
                t3 = st.number_input("To Account ID",   step=1, min_value=1)
                t4 = st.text_input("Référence")
                t5 = st.date_input("Date de transfert")
                if st.form_submit_button("Ajouter"):
                    add_transfer(t1, t2, t3, t4, t5)
                    st.success("Transfer ajouté")
            else:  # Check
                c1 = st.number_input("Transaction ID", step=1, min_value=1)
                c2 = st.text_input("Numéro de chèque")
                c3 = st.text_input("Bénéficiaire")
                c4 = st.date_input("Date d'émission")
                c5 = st.date_input("Date d'encaissement")
                if st.form_submit_button("Ajouter"):
                    add_check(c1, c2, c3, c4, c5)
                    st.success("Check ajouté")

    st.markdown("---")
    st.subheader(f"Mettre à jour un {table}")
    with st.form(f"form_up_{table}", clear_on_submit=True):
        uid = st.number_input("ID", step=1, min_value=1)
        if table == "Transaction":
            f1 = st.number_input("Montant", format="%.2f")
            f2 = st.text_input("Statut")
            if st.form_submit_button("Mettre à jour"):
                update_transaction(uid, amount=f1, status=f2)
                st.success("Mis à jour")
        elif table == "Transfer":
            f1 = st.text_input("Référence")
            if st.form_submit_button("Mettre à jour"):
                update_transfer(uid, transfer_reference=f1)
                st.success("Mis à jour")
        else:
            f1 = st.text_input("Bénéficiaire")
            if st.form_submit_button("Mettre à jour"):
                update_check(uid, payee_name=f1)
                st.success("Mis à jour")

    st.subheader(f"Supprimer un {table}")
    with st.form(f"form_del_{table}", clear_on_submit=True):
        did = st.number_input("ID à supprimer", step=1, min_value=1)
        if st.form_submit_button("Supprimer"):
            if table == "Transaction":
                delete_transaction(did)
            elif table == "Transfer":
                delete_transfer(did)
            else:
                delete_check(did)
            st.success("Supprimé")

# --- PAGE: Rapports ---
elif page == "📈 Rapports":
    st.title("📈 Rapports")
    st.subheader("Totaux mensuels par type")
    df_monthly = get_monthly_totals_by_type()
    st.dataframe(df_monthly, use_container_width=True)

    st.markdown("---")
    st.subheader("Transactions > Seuil")
    seuil = st.number_input("Seuil montant", value=1_000_000, step=100_000, format="%.2f")
    df_large = get_large_transactions(threshold=seuil)
    st.dataframe(df_large, use_container_width=True)

# --- PAGE: Procédures stockées ---
else:
    st.title("⚙️ Procédures stockées")
    col1, col2 = st.columns(2)

    with col1.expander("🔄 update_inactive_accounts"):
        if st.button("Exécuter"):
            run_update_inactive_accounts()
            st.success("Procédure exécutée")

    with col2.expander("⛔ check_and_block_account_if_overdraft"):
        acc_id = st.number_input("Account ID", step=1, min_value=1, key="proc_acc")
        seuil = st.number_input("Seuil négatif", value=-100.00, format="%.2f", key="proc_seuil")
        if st.button("Exécuter", key="btn_proc"):
            run_check_and_block(acc_id, seuil)
            st.success(f"Compte {acc_id} vérifié et bloqué si nécessaire")
