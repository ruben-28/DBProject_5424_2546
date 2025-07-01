import streamlit as st
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from stage5 import Transaction, Transfer, Check, Session

# --- PARAMÈTRES D'AUTHENTIFICATION ---
VALID_USERNAME = "ruben"
VALID_PASSWORD = "2810"

# Initialisation de l'état de session
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# Écran de connexion
if not st.session_state['logged_in']:
    st.title("🔐 Connexion requise")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state['logged_in'] = True
        else:
            st.error("Identifiants invalides")
    st.stop()  # arrête l'exécution tant que l'utilisateur n'est pas connecté

# Configuration de la page (après authentification)
st.set_page_config(page_title="Gestion Transactions", layout="wide")
tab_crud, tab_reports = st.tabs(["CRUD", "Rapports"])


# === ONGLET CRUD ===
with tab_crud:
    table = st.sidebar.selectbox("Sélectionner la table", ["Transaction", "Transfer", "Check"])
    key = table if table == "Transaction" else table.lower()
    st.header(f"Gérer les {table}s")

    # Récupération des données
    def fetch_data(table_name):
        with Session() as session:
            if table_name == "Transaction":
                rows = session.query(Transaction).all()
                return pd.DataFrame([{
                    "transaction_id":   r.transaction_id,
                    "account_id":       r.account_id_FK,
                    "type_id":          r.transaction_type,
                    "transaction_date": r.transaction_date,
                    "amount":           float(r.amount),
                    "description":      r.description,
                    "status":           r.status
                } for r in rows])

            elif table_name == "transfer":
                rows = session.query(Transfer).all()
                return pd.DataFrame([{
                    "transfer_id":     r.transfer_id,
                    "transaction_id":  r.transaction_id,
                    "from_account":    r.from_account_id_fk,
                    "to_account":      r.to_account_id_fk,
                    "reference":       r.transfer_reference,
                    "transfer_date":   r.transfer_date
                } for r in rows])

            elif table_name == "check":
                rows = session.query(Check).all()
                return pd.DataFrame([{
                    "checks_id":       r.checks_id,
                    "transaction_id":  r.transaction_id,
                    "checks_number":   r.checks_number,
                    "payee_name":      r.payee_name,
                    "issue_date":      r.issue_date,
                    "clearance_date":  r.clearance_date
                } for r in rows])

        return pd.DataFrame()

    df = fetch_data(key)
    if df.empty:
        st.write("Aucune donnée à afficher.")
    else:
        st.dataframe(df)

    # Fonctions CRUD
    def add_transaction(account_id, type_id, date, amount, description, status):
        with Session() as session:
            try:
                tx = Transaction(
                    account_id_FK=int(account_id),
                    transaction_type=int(type_id),
                    transaction_date=date,
                    amount=float(amount),
                    description=description,
                    status=status
                )
                session.add(tx)
                session.commit()
                st.success("Transaction ajoutée")
            except Exception as e:
                session.rollback()
                st.error(f"Erreur ajout Transaction : {e}")

    def update_transaction(tx_id, account_id, type_id, date, amount, description, status):
        with Session() as session:
            tx = session.get(Transaction, tx_id)
            if not tx:
                st.error("Transaction non trouvée")
                return
            try:
                tx.account_id_FK    = account_id
                tx.transaction_type = type_id
                tx.transaction_date = date
                tx.amount           = amount
                tx.description      = description
                tx.status           = status
                session.commit()
                st.success("✅ Transaction mise à jour")
            except Exception as e:
                session.rollback()
                st.error(f"⚠ Erreur mise à jour Transaction : {e}")

    def delete_transaction(tx_id):
        with Session() as session:
            try:
                session.execute(
                    text("DELETE FROM transaction_audit WHERE transaction_id = :id"),
                    {"id": tx_id}
                )
                session.query(Transfer).filter(Transfer.transaction_id == tx_id).delete(synchronize_session=False)
                session.query(Check).filter(Check.transaction_id == tx_id).delete(synchronize_session=False)
                tx = session.get(Transaction, tx_id)
                if not tx:
                    st.error("Transaction non trouvée")
                    return
                session.delete(tx)
                session.commit()
                st.success("Transaction et dépendances supprimées")
            except IntegrityError:
                session.rollback()
                st.error("⛔ Impossible de supprimer : contraintes FK")
            except Exception as e:
                session.rollback()
                st.error(f"⚠ Erreur suppression Transaction : {e}")

    def add_transfer(transaction_id, from_account, to_account, reference, transfer_date):
        with Session() as session:
            try:
                tr = Transfer(
                    transaction_id=int(transaction_id),
                    from_account_id_fk=int(from_account),
                    to_account_id_fk=int(to_account),
                    transfer_reference=reference,
                    transfer_date=transfer_date
                )
                session.add(tr)
                session.commit()
                st.success("Transfer ajouté")
            except Exception as e:
                session.rollback()
                st.error(f"Erreur ajout Transfer : {e}")

    def update_transfer(tr_id, transaction_id, from_account, to_account, reference, transfer_date):
        with Session() as session:
            tr = session.get(Transfer, int(tr_id))
            if not tr:
                st.error("Transfer non trouvé")
                return
            try:
                tr.transaction_id      = int(transaction_id)
                tr.from_account_id_fk  = int(from_account)
                tr.to_account_id_fk    = int(to_account)
                tr.transfer_reference  = reference
                tr.transfer_date       = transfer_date
                session.commit()
                st.success("Transfer mise à jour")
            except Exception as e:
                session.rollback()
                st.error(f"Erreur mise à jour Transfer : {e}")

    def delete_transfer(tr_id):
        with Session() as session:
            tr = session.get(Transfer, int(tr_id))
            if not tr:
                st.error("Transfer non trouvé")
                return
            try:
                session.delete(tr)
                session.commit()
                st.success("Transfer supprimé")
            except IntegrityError:
                session.rollback()
                st.error("Suppression impossible : contraintes FK")

    def add_check(transaction_id, check_number, payee_name, issue_date, clearance_date):
        with Session() as session:
            try:
                chk = Check(
                    transaction_id=int(transaction_id),
                    checks_number=check_number,
                    payee_name=payee_name,
                    issue_date=issue_date,
                    clearance_date=clearance_date
                )
                session.add(chk)
                session.commit()
                st.success("Check ajouté")
            except Exception as e:
                session.rollback()
                st.error(f"Erreur ajout Check : {e}")

    def update_check(chk_id, transaction_id, check_number, payee_name, issue_date, clearance_date):
        with Session() as session:
            chk = session.get(Check, int(chk_id))
            if not chk:
                st.error("Check non trouvé")
                return
            try:
                chk.transaction_id  = int(transaction_id)
                chk.checks_number   = check_number
                chk.payee_name      = payee_name
                chk.issue_date      = issue_date
                chk.clearance_date  = clearance_date
                session.commit()
                st.success("Check mise à jour")
            except Exception as e:
                session.rollback()
                st.error(f"Erreur mise à jour Check : {e}")

    def delete_check(chk_id):
        with Session() as session:
            chk = session.get(Check, int(chk_id))
            if not chk:
                st.error("Check non trouvé")
                return
            try:
                session.delete(chk)
                session.commit()
                st.success("Check supprimé")
            except IntegrityError:
                session.rollback()
                st.error("Suppression impossible : contraintes FK")

    # Formulaires CRUD
    if table == "Transaction":
        with st.expander("➕ Ajouter Transaction"):
            data = {
                'account_id':  st.number_input("Account ID", min_value=1),
                'type_id':     st.number_input("Type ID",    min_value=1),
                'date':        st.date_input("Date"),
                'amount':      st.text_input("Amount"),
                'description': st.text_input("Description"),
                'status':      st.text_input("Status")
            }
            if st.button("Ajouter"):
                add_transaction(**data)

        with st.expander("✏ Mettre à jour Transaction"):
            with st.form("update_tx_form"):
                tx_id       = st.number_input("Transaction ID", min_value=1, key="update_tx_id")
                account_id  = st.number_input("Account ID",       min_value=1, key="update_account_id")
                type_id     = st.number_input("Type ID",          min_value=1, key="update_type_id")
                date        = st.date_input("Date",               key="update_date")
                amount      = st.number_input("Montant",          min_value=0.0, format="%.2f", key="update_amount")
                description = st.text_input("Description",       key="update_description")
                status      = st.text_input("Statut",            key="update_status")
                if st.form_submit_button("Mettre à jour"):
                    update_transaction(tx_id, account_id, type_id, date, amount, description, status)

        with st.expander("🗑 Supprimer Transaction"):
            tx_id_del = st.number_input("Transaction ID à supprimer", min_value=1, key="del_tx_id")
            if st.button("Supprimer"):
                delete_transaction(tx_id_del)

    elif table == "Transfer":
        with st.expander("➕ Ajouter Transfer"):
            data = {
                'transaction_id': st.number_input("Transaction ID",    min_value=1),
                'from_account':   st.number_input("From Account ID",   min_value=1),
                'to_account':     st.number_input("To Account ID",     min_value=1),
                'reference':      st.text_input("Reference"),
                'transfer_date':  st.date_input("Transfer Date")
            }
            if st.button("Ajouter Transfer"):
                add_transfer(**data)

        with st.expander("✏ Mettre à jour Transfer"):
            with st.form("update_tr_form"):
                tr_id          = st.number_input("Transfer ID",      min_value=1, key="upd_tr_id")
                transaction_id = st.number_input("Transaction ID",   min_value=1, key="upd_tr_tx_id")
                from_account   = st.number_input("From Account ID",  min_value=1, key="upd_tr_from")
                to_account     = st.number_input("To Account ID",    min_value=1, key="upd_tr_to")
                reference      = st.text_input("Reference",         key="upd_tr_ref")
                transfer_date  = st.date_input("Transfer Date",     key="upd_tr_date")
                if st.form_submit_button("Mettre à jour Transfer"):
                    update_transfer(tr_id, transaction_id, from_account, to_account, reference, transfer_date)

        with st.expander("🗑 Supprimer Transfer"):
            tr_id_del = st.number_input("Transfer ID à supprimer", min_value=1, key="del_tr_id")
            if st.button("Supprimer Transfer"):
                delete_transfer(tr_id_del)

    else:  # Check
        with st.expander("➕ Ajouter Check"):
            data = {
                'transaction_id': st.number_input("Transaction ID", min_value=1),
                'check_number':   st.text_input("Check Number"),
                'payee_name':     st.text_input("Payee Name"),
                'issue_date':     st.date_input("Issue Date"),
                'clearance_date': st.date_input("Clearance Date")
            }
            if st.button("Ajouter Check"):
                add_check(**data)

        with st.expander("✏️ Mettre à jour Check"):
            with st.form("update_chk_form"):
                chk_id         = st.number_input("Check ID",        min_value=1, key="upd_chk_id")
                transaction_id = st.number_input("Transaction ID",  min_value=1, key="upd_chk_tx_id")
                check_number   = st.text_input("Check Number",     key="upd_chk_number")
                payee_name     = st.text_input("Payee Name",       key="upd_chk_payee")
                issue_date     = st.date_input("Issue Date",       key="upd_chk_issue")
                clearance_date = st.date_input("Clearance Date",   key="upd_chk_clear")
                if st.form_submit_button("Mettre à jour Check"):
                    update_check(chk_id, transaction_id, check_number, payee_name, issue_date, clearance_date)

        with st.expander("🗑 Supprimer Check"):
            chk_id_del = st.number_input("Check ID à supprimer", min_value=1, key="del_chk_id")
            if st.button("Supprimer Check"):
                delete_check(chk_id_del)


# === ONGLET RAPPORTS ===
with tab_reports:
    st.header("Rapports SQL")

    def get_monthly_totals_by_type():
        sql = """
        SELECT
          t.transaction_type    AS transaction_type,
          TO_CHAR(t.transaction_date::DATE, 'YYYY-MM') AS year_month,
          SUM(t.amount)        AS total_amount
        FROM "Transaction" t
        JOIN transfer tr ON t.transaction_id = tr.transaction_id
        GROUP BY
          t.transaction_type,
          year_month
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
        ORDER BY t.amount DESC;
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

    with st.expander("📊 Totaux mensuels par type"):
        df_monthly = get_monthly_totals_by_type()
        if df_monthly.empty:
            st.write("Aucun résultat.")
        else:
            st.dataframe(df_monthly)

    with st.expander("💰 Transactions > 1 000 000"):
        seuil = st.number_input("Seuil montant", value=1_000_000, step=100_000)
        df_large = get_large_transactions(threshold=seuil)
        if df_large.empty:
            st.write("Aucun montant supérieur à ce seuil.")
        else:
            st.dataframe(df_large)

    with st.expander("🔄 Mettre à jour comptes inactifs"):
        if st.button("Exécuter update_inactive_accounts"):
            run_update_inactive_accounts()
            st.success("Procédure update_inactive_accounts exécutée")

    with st.expander("⛔ Vérifier et bloquer si découvert"):
        acc_id = st.number_input("Account ID", min_value=1, step=1)
        thresh = st.number_input("Seuil négatif", value=-100.00, format="%.2f")
        if st.button("Exécuter check_and_block_account_if_overdraft"):
            run_check_and_block(acc_id, thresh)
            st.success(f"Procédure check_and_block_account_if_overdraft exécutée pour compte {acc_id}")
