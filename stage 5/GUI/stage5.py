from sqlalchemy import (
    create_engine, Column, Integer, String, Date, Numeric, ForeignKey, Sequence
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# 1) Chaîne de connexion (à adapter)
DB_USER = "ruben"
DB_PASSWORD = "2810"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "mydatabase"
CONN_STR = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 2) Base et engine
Base = declarative_base()
engine = create_engine(CONN_STR, echo=True)
Session = sessionmaker(bind=engine)


# 3) Modèles ORM
class Transaction(Base):
    __tablename__ = "Transaction"
    transaction_id = Column(
        Integer,
        Sequence('transaction_id_seq'),
        primary_key=True,
        server_default=Sequence('transaction_id_seq').next_value()
    )
    account_id_FK    = Column(Integer, nullable=False)
    transaction_type = Column(Integer, nullable=False)
    transaction_date = Column(Date,    nullable=False)
    amount           = Column(Numeric(12, 2), nullable=False)
    description      = Column(String(255))
    status           = Column(String(50))
    transfers        = relationship("Transfer", back_populates="transaction")
    checks           = relationship("Check",    back_populates="transaction")


class Transfer(Base):
    __tablename__ = "transfer"
    transfer_id         = Column(
        Integer,
        Sequence('transfer_id_seq'),
        primary_key=True,
        server_default=Sequence('transfer_id_seq').next_value()
    )
    transaction_id      = Column(Integer, ForeignKey("Transaction.transaction_id"), nullable=False)
    from_account_id_fk  = Column(Integer, nullable=False)
    to_account_id_fk    = Column(Integer, nullable=False)
    transfer_reference  = Column(String(100))
    transfer_date       = Column(Date, nullable=False)
    transaction         = relationship("Transaction", back_populates="transfers")


class Check(Base):
    __tablename__ = "checks"
    checks_id       = Column(
        Integer,
        Sequence('checks_id_seq'),
        primary_key=True,
        server_default=Sequence('checks_id_seq').next_value()
    )
    transaction_id  = Column(Integer, ForeignKey("Transaction.transaction_id"), nullable=False)
    checks_number   = Column(String(50))
    payee_name      = Column(String(100))
    issue_date      = Column(Date, nullable=False)
    clearance_date  = Column(Date)
    transaction     = relationship("Transaction", back_populates="checks")


# --- CRUD UTILS --------------------------------------------------------------
def add_transaction(account_id, type_id, date, amount, description, status):
    """Insert a new Transaction and return its id."""
    with Session() as session:
        obj = Transaction(
            account_id_FK=account_id,
            transaction_type=type_id,
            transaction_date=date,
            amount=amount,
            description=description,
            status=status,
        )
        session.add(obj)
        session.commit()
        return obj.transaction_id


def update_transaction(t_id, **fields):
    """Update a Transaction by id."""
    with Session() as session:
        obj = session.get(Transaction, t_id)
        if not obj:
            return False
        for k, v in fields.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        session.commit()
        return True


def delete_transaction(t_id):
    """Delete a Transaction by id."""
    with Session() as session:
        obj = session.get(Transaction, t_id)
        if not obj:
            return False
        session.delete(obj)
        session.commit()
        return True


def add_transfer(t_id, from_acc, to_acc, ref, date):
    with Session() as session:
        obj = Transfer(
            transaction_id=t_id,
            from_account_id_fk=from_acc,
            to_account_id_fk=to_acc,
            transfer_reference=ref,
            transfer_date=date,
        )
        session.add(obj)
        session.commit()
        return obj.transfer_id


def update_transfer(tr_id, **fields):
    with Session() as session:
        obj = session.get(Transfer, tr_id)
        if not obj:
            return False
        for k, v in fields.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        session.commit()
        return True


def delete_transfer(tr_id):
    with Session() as session:
        obj = session.get(Transfer, tr_id)
        if not obj:
            return False
        session.delete(obj)
        session.commit()
        return True


def add_check(t_id, number, payee, issue_date, clearance_date):
    with Session() as session:
        obj = Check(
            transaction_id=t_id,
            checks_number=number,
            payee_name=payee,
            issue_date=issue_date,
            clearance_date=clearance_date,
        )
        session.add(obj)
        session.commit()
        return obj.checks_id


def update_check(c_id, **fields):
    with Session() as session:
        obj = session.get(Check, c_id)
        if not obj:
            return False
        for k, v in fields.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        session.commit()
        return True


def delete_check(c_id):
    with Session() as session:
        obj = session.get(Check, c_id)
        if not obj:
            return False
        session.delete(obj)
        session.commit()
        return True


# 4) Créer les tables si on lance ce script directement
if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Tables créées.")
