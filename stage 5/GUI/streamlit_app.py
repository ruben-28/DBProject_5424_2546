from xmlrpc.client import DateTime

import streamlit as st
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date
from stage5 import Transaction, Transfer, Check, Account, Session


st.set_page_config(
    page_title="Gestion Transactions",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stButton>button {border-radius:5px;}
    .stTextInput>div>div>input {border-radius:5px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- PARAMÈTRES D'AUTHENTIFICATION ---
VALID_USERNAME = "ruben"
VALID_PASSWORD = "2810"


# Initialisation de l'état de session
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False


if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align:center'>🔐 Connexion requise</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Nom d'utilisateur")
            password = st.text_input("Mot de passe", type="password")
            if st.form_submit_button("Se connecter"):
                if username == VALID_USERNAME and password == VALID_PASSWORD:
                    st.session_state['logged_in'] = True
                else:
                    st.error("Identifiants invalides")
    st.stop()  # arrête l'exécution tant que l'utilisateur n'est pas connecté

# Configuration de la page (après authentification)
st.title("🏦 Gestion des Transactions")
tab_crud, tab_reports = st.tabs(["CRUD", "Rapports"])


# === ONGLET CRUD ===
with tab_crud:
    table = st.sidebar.selectbox(
        "Sélectionner la table",
        ["Transaction", "Transfer", "Check", "Account"]
    )

    key = table if table == "Transaction" else table.lower()


    # Récupération des données
    def fetch_data(table_name):
        with Session() as session:
            if table_name == "Transaction":
                rows = session.query(Transaction).all()
                return pd.DataFrame([{
                    "transaction_id": r.transaction_id,
                    "account_id": r.account_id_FK,
                    "type_name": r.transaction_type,
                    "transaction_date": r.transaction_date,
                    "amount": float(r.amount),
                    "description": r.description,
                    "status": r.status
                } for r in rows])

            elif table_name == "transfer":
                rows = session.query(Transfer).all()
                return pd.DataFrame([{
                    "transfer_id": r.transfer_id,
                    "transaction_id": r.transaction_id,
                    "from_account": r.from_account_id_fk,
                    "to_account": r.to_account_id_fk,
                    "reference": r.transfer_reference,
                    "transfer_date": r.transfer_date
                } for r in rows])

            elif table_name == "check":
                rows = session.query(Check).all()
                return pd.DataFrame([{
                    "checks_id": r.checks_id,
                    "transaction_id": r.transaction_id,
                    "checks_number": r.checks_number,
                    "payee_name": r.payee_name,
                    "issue_date": r.issue_date,
                    "clearance_date": r.clearance_date
                } for r in rows])

            elif table_name == "account":
                rows = session.query(Account).all()
                return pd.DataFrame([
                    {
                        "account_id": r.account_id,
                        "customer_id": r.customer_id,
                        "account_num": r.account_num,
                        "opening_date": r.opening_date,
                        "current_balance": float(r.current_balance) if r.current_balance is not None else None,
                        "status": r.status,
                        "account_type": r.account_type
                    } for r in rows
                ])

            elif table_name == "account":
                rows = session.query(Account).all()
                return pd.DataFrame([
                    {
                        "account_id": r.account_id,
                        "customer_id": r.customer_id,
                        "account_num": r.account_num,
                        "opening_date": r.opening_date,
                        "current_balance": float(r.current_balance) if r.current_balance is not None else None,
                        "status": r.status,
                        "account_type": r.account_type
                    } for r in rows
                ])

        return pd.DataFrame()


    if 'last_table' not in st.session_state or st.session_state.last_table != key:
        st.session_state.last_table = key
        st.session_state.df_crud = fetch_data(key)

    # 1) Initialisation en session (chargement unique au premier tour)
    if 'df_crud' not in st.session_state:
        st.session_state.df_crud = fetch_data(key)

    # 2) Bouton “🔄 Rafraîchir” pour recharger à la volée
    if st.button("🔄 Rafraîchir"):
        st.session_state.df_crud = fetch_data(key)
        st.success("Tableau mis à jour")

    # 3) Affichage du DataFrame stocké
    if st.session_state.df_crud.empty:
        st.write("Aucune donnée à afficher.")
    else:
        st.dataframe(st.session_state.df_crud)
    st.header(f"Gérer les {table}s")





    # Fonctions CRUD
    def add_transaction(account_id, type_name, date, amount, description, status):
        with Session() as session:
            try:
                if not status or status.strip() == "":
                    status = "pending"
                    st.info("ℹ Statut automatiquement défini à 'pending'")
                tx = Transaction(
                    account_id_FK=int(account_id),
                    transaction_type=int(type_name),
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

    def update_transaction(tx_id, account_id, type_name, date, amount, description, status):
        with Session() as session:
            tx = session.get(Transaction, tx_id)
            if not tx:
                st.error("Transaction non trouvée")
                return
            try:
                tx.account_id_FK    = account_id
                tx.transaction_type = type_name
                tx.transaction_date = date
                tx.amount           = amount
                tx.description      = description
                tx.status           = status
                session.commit()
                st.success("✅ Transaction mise à jour")
            except Exception as e:
                session.rollback()
                st.error(f"⚠ Erreur mise à jour Transaction : {e}")


    def get_transaction_by_id(tx_id):
        with Session() as session:
            tx = session.get(Transaction, tx_id)
            if tx:
                return {
                    'account_id': tx.account_id_FK,
                    'type_name': tx.transaction_type,
                    'date': tx.transaction_date,
                    'amount': float(tx.amount),
                    'description': tx.description or "",
                    'status': tx.status or ""
                }
        return None

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


    def get_transfer_by_id(tr_id):
        with Session() as session:
            tr = session.get(Transfer, tr_id)
            if tr:
                return {
                    'transaction_id': tr.transaction_id,
                    'from_account': tr.from_account_id_fk,
                    'to_account': tr.to_account_id_fk,
                    'reference': tr.transfer_reference or "",
                    'transfer_date': tr.transfer_date
                }
        return None

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


    def get_check_by_id(chk_id):
        with Session() as session:
            chk = session.get(Check, chk_id)
            if chk:
                return {
                    'transaction_id': chk.transaction_id,
                    'check_number': chk.checks_number or "",
                    'payee_name': chk.payee_name or "",
                    'issue_date': chk.issue_date,
                    'clearance_date': chk.clearance_date
                }
        return None


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

    def add_account(customer_id, account_num, opening_date, current_balance, status, account_type):
        with Session() as session:
            try:
                acc = Account(
                    customer_id=customer_id,
                    account_num=account_num,
                    opening_date=opening_date,
                    current_balance=current_balance,
                    status=status,
                    account_type=account_type
                )
                session.add(acc)
                session.commit()
                st.success("Account ajouté")
            except Exception as e:
                session.rollback()
                st.error(f"Erreur ajout Account : {e}")

    def update_account(acc_id, customer_id, account_num, opening_date, current_balance, status, account_type):
        with Session() as session:
            acc = session.get(Account, int(acc_id))
            if not acc:
                st.error("Account non trouvé")
                return
            try:
                acc.customer_id     = customer_id
                acc.account_num     = account_num
                acc.opening_date    = opening_date
                acc.current_balance = current_balance
                acc.status          = status
                acc.account_type    = account_type
                session.commit()
                st.success("Account mise à jour")
            except Exception as e:
                session.rollback()
                st.error(f"Erreur mise à jour Account : {e}")

    def delete_account(acc_id):
        with Session() as session:
            acc = session.get(Account, int(acc_id))
            if not acc:
                st.error("Account non trouvé")
                return
            try:
                session.delete(acc)
                session.commit()
                st.success("Account supprimé")
            except IntegrityError:
                session.rollback()
                st.error("Suppression impossible : contraintes FK")

    def add_account(customer_id, account_num, opening_date, current_balance, status, account_type):
        with Session() as session:
            try:
                acc = Account(
                    customer_id=customer_id,
                    account_num=account_num,
                    opening_date=opening_date,
                    current_balance=current_balance,
                    status=status,
                    account_type=account_type
                )
                session.add(acc)
                session.commit()
                st.success("Account ajouté")
            except Exception as e:
                session.rollback()
                st.error(f"Erreur ajout Account : {e}")

    def update_account(acc_id, customer_id, account_num, opening_date, current_balance, status, account_type):
        with Session() as session:
            acc = session.get(Account, int(acc_id))
            if not acc:
                st.error("Account non trouvé")
                return
            try:
                acc.customer_id     = customer_id
                acc.account_num     = account_num
                acc.opening_date    = opening_date
                acc.current_balance = current_balance
                acc.status          = status
                acc.account_type    = account_type
                session.commit()
                st.success("Account mise à jour")
            except Exception as e:
                session.rollback()
                st.error(f"Erreur mise à jour Account : {e}")


    def get_account_by_id(acc_id):
        with Session() as session:
            acc = session.get(Account, acc_id)
            if acc:
                return {
                    'customer_id': acc.customer_id or "",
                    'account_num': acc.account_num or "",
                    'opening_date': acc.opening_date,
                    'current_balance': float(acc.current_balance) if acc.current_balance is not None else 0.0,
                    'status': acc.status or "",
                    'account_type': acc.account_type or ""
                }
        return None

    def delete_account(acc_id):
        with Session() as session:
            acc = session.get(Account, int(acc_id))
            if not acc:
                st.error("Account non trouvé")
                return
            try:
                session.delete(acc)
                session.commit()
                st.success("Account supprimé")
            except IntegrityError:
                session.rollback()
                st.error("Suppression impossible : contraintes FK")

    # Formulaires CRUD
    if table == "Transaction":
        with st.expander("➕ Ajouter Transaction"):
            data = {
                'account_id':  st.number_input("Account ID", min_value=1),
                'type_name':     st.text_input("Type Name"),
                'date':        st.date_input("Date"),
                'amount':      st.text_input("Amount"),
                'description': st.text_input("Description"),
                'status':      st.text_input("Status")
            }
            if st.button("Ajouter"):
                add_transaction(**data)

        with st.expander("✏️ Mettre à jour Transaction"):
            # Étape 1: Saisir l'ID pour charger les données
            tx_id_to_load = st.number_input("Entrez l'ID de la Transaction à modifier", min_value=1, key="load_tx_id")

            # Initialiser les valeurs par défaut
            default_values = {
                'account_id': 1,
                'type_name': "",
                'date': datetime.now().date(),
                'amount': 0.0,
                'description': "",
                'status': ""
            }

            # Charger les données si l'ID est fourni
            if tx_id_to_load:
                tx_data = get_transaction_by_id(tx_id_to_load)
                if tx_data:
                    default_values.update(tx_data)
                    st.success(f"✅ Données chargées pour la Transaction ID: {tx_id_to_load}")
                else:
                    st.warning(f"⚠ Aucune transaction trouvée avec l'ID: {tx_id_to_load}")

            # Formulaire avec valeurs pré-remplies
            with st.form("update_tx_form"):
                account_id = st.number_input("Account ID", min_value=1, value=default_values['account_id'],
                                             key="update_account_id")
                type_name = st.text_input("Type Name",value=default_values['type_name'],key="update_type_name" )
                date = st.date_input("Date", value=default_values['date'], key="update_date")
                amount = st.number_input("Montant", min_value=0.0, format="%.2f", value=default_values['amount'],
                                         key="update_amount")
                description = st.text_input("Description", value=default_values['description'],
                                            key="update_description")
                status = st.text_input("Statut", value=default_values['status'], key="update_status")

                if st.form_submit_button("Mettre à jour"):
                    if tx_id_to_load:
                        update_transaction(tx_id_to_load, account_id, type_name, date, amount, description, status)
                    else:
                        st.error("Veuillez d'abord entrer un ID de transaction valide")

        with st.expander("🗑️ Supprimer Transaction"):
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

        with st.expander("✏️ Mettre à jour Transfer"):
            # Étape 1: Saisir l'ID pour charger les données
            tr_id_to_load = st.number_input("Entrez l'ID du Transfer à modifier", min_value=1, key="load_tr_id")

            # Initialiser les valeurs par défaut
            default_values = {
                'transaction_id': 1,
                'from_account': 1,
                'to_account': 1,
                'reference': "",
                'transfer_date': datetime.now().date()
            }

            # Charger les données si l'ID est fourni
            if tr_id_to_load:
                tr_data = get_transfer_by_id(tr_id_to_load)
                if tr_data:
                    default_values.update(tr_data)
                    st.success(f"✅ Données chargées pour le Transfer ID: {tr_id_to_load}")
                else:
                    st.warning(f"⚠ Aucun transfer trouvé avec l'ID: {tr_id_to_load}")

            with st.form("update_tr_form"):
                transaction_id = st.number_input("Transaction ID", min_value=1, value=default_values['transaction_id'],
                                                 key="upd_tr_tx_id")
                from_account = st.number_input("From Account ID", min_value=1, value=default_values['from_account'],
                                               key="upd_tr_from")
                to_account = st.number_input("To Account ID", min_value=1, value=default_values['to_account'],
                                             key="upd_tr_to")
                reference = st.text_input("Reference", value=default_values['reference'], key="upd_tr_ref")
                transfer_date = st.date_input("Transfer Date", value=default_values['transfer_date'], key="upd_tr_date")

                if st.form_submit_button("Mettre à jour Transfer"):
                    if tr_id_to_load:
                        update_transfer(tr_id_to_load, transaction_id, from_account, to_account, reference,
                                        transfer_date)
                    else:
                        st.error("Veuillez d'abord entrer un ID de transfer valide")


        with st.expander("🗑️ Supprimer Transfer"):
            tr_id_del = st.number_input("Transfer ID à supprimer", min_value=1, key="del_tr_id")
            if st.button("Supprimer Transfer"):
                delete_transfer(tr_id_del)


    elif table == "Account":
        with st.expander("➕ Ajouter Account"):
            data = {
                'customer_id':     st.text_input("Customer ID"),
                'account_num':     st.text_input("Account Number"),
                'opening_date':    st.date_input("Opening Date"),
                'current_balance': st.number_input("Current Balance", format="%.2f"),
                'status':          st.text_input("Status"),
                'account_type':    st.text_input("Account Type")
            }
            if st.button("Ajouter Account"):
                add_account(**data)

        with st.expander("✏️ Mettre à jour Account"):
            # Étape 1: Saisir l'ID pour charger les données
            acc_id_to_load = st.number_input("Entrez l'ID de l'Account à modifier", min_value=1, key="load_acc_id")

            # Initialiser les valeurs par défaut
            default_values = {
                'customer_id': "",
                'account_num': "",
                'opening_date': datetime.now().date(),
                'current_balance': 0.0,
                'status': "",
                'account_type': ""
            }

            # Charger les données si l'ID est fourni
            if acc_id_to_load:
                acc_data = get_account_by_id(acc_id_to_load)
                if acc_data:
                    default_values.update(acc_data)
                    st.success(f"✅ Données chargées pour l'Account ID: {acc_id_to_load}")
                else:
                    st.warning(f"⚠ Aucun account trouvé avec l'ID: {acc_id_to_load}")

            with st.form("update_acc_form"):
                customer_id = st.text_input("Customer ID", value=default_values['customer_id'], key="upd_cust")
                account_num = st.text_input("Account Number", value=default_values['account_num'], key="upd_acc_num")
                opening_date = st.date_input("Opening Date", value=default_values['opening_date'], key="upd_open")
                current_balance = st.number_input("Current Balance", format="%.2f",
                                                  value=default_values['current_balance'], key="upd_bal")
                status = st.text_input("Status", value=default_values['status'], key="upd_status")
                account_type = st.text_input("Account Type", value=default_values['account_type'], key="upd_acc_type")

                if st.form_submit_button("Mettre à jour Account"):
                    if acc_id_to_load:
                        update_account(acc_id_to_load, customer_id, account_num, opening_date, current_balance, status,
                                       account_type)
                    else:
                        st.error("Veuillez d'abord entrer un ID d'account valide")
        with st.expander("🗑️ Supprimer Account"):
            acc_id_del = st.number_input("Account ID à supprimer", min_value=1, key="del_acc_id")
            if st.button("Supprimer Account"):
                delete_account(acc_id_del)

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
            # Étape 1: Saisir l'ID pour charger les données
            chk_id_to_load = st.number_input("Entrez l'ID du Check à modifier", min_value=1, key="load_chk_id")

            # Initialiser les valeurs par défaut
            default_values = {
                'transaction_id': 1,
                'check_number': "",
                'payee_name': "",
                'issue_date': datetime.now().date(),
                'clearance_date': datetime.now().date()
            }

            # Charger les données si l'ID est fourni
            if chk_id_to_load:
                chk_data = get_check_by_id(chk_id_to_load)
                if chk_data:
                    default_values.update(chk_data)
                    st.success(f"✅ Données chargées pour le Check ID: {chk_id_to_load}")
                else:
                    st.warning(f"⚠ Aucun check trouvé avec l'ID: {chk_id_to_load}")

            with st.form("update_chk_form"):
                transaction_id = st.number_input("Transaction ID", min_value=1, value=default_values['transaction_id'],
                                                 key="upd_chk_tx_id")
                check_number = st.text_input("Check Number", value=default_values['check_number'], key="upd_chk_number")
                payee_name = st.text_input("Payee Name", value=default_values['payee_name'], key="upd_chk_payee")
                issue_date = st.date_input("Issue Date", value=default_values['issue_date'], key="upd_chk_issue")
                clearance_date = st.date_input("Clearance Date", value=default_values['clearance_date'],
                                               key="upd_chk_clear")

                if st.form_submit_button("Mettre à jour Check"):
                    if chk_id_to_load:
                        update_check(chk_id_to_load, transaction_id, check_number, payee_name, issue_date,
                                     clearance_date)
                    else:
                        st.error("Veuillez d'abord entrer un ID de check valide")
        with st.expander("🗑️ Supprimer Check"):
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

    def run_check_and_block( threshold):
        with Session() as session:
            session.execute(
                text("CALL check_and_block_overdrafts( :threshold)"),
                { "threshold": threshold}
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

        thresh = st.number_input("Seuil négatif", value=-100.00, format="%.2f")
        if st.button("Exécuter check_and_block_account_if_overdraft"):
            run_check_and_block( thresh)
            st.success(f"Procédure check_and_block_overdrafts exécutée pour tous comptes (< {thresh})")
