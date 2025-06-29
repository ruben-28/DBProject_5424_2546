# your_models.py
from sqlalchemy import (
    create_engine, Column, Integer, String, Date, Numeric, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import Sequence

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


# 3) Tes modèles ORM
class Transaction(Base):
    __tablename__ = "Transaction"  # ← obligatoire
    transaction_id = Column(
        Integer,
        Sequence('transaction_id_seq'),  # nom exact de ta séquence
        primary_key=True,
        server_default=Sequence('transaction_id_seq').next_value()
    )
    account_id_FK = Column(Integer, nullable=False)
    transaction_type = Column(Integer, nullable=False)
    transaction_date = Column(Date, nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(String(255))
    status = Column(String(50))
    transfers = relationship("Transfer", back_populates="transaction")
    checks = relationship("Check", back_populates="transaction")


class Transfer(Base):
    __tablename__ = "transfer"
    transfer_id = Column(

        Integer,

        Sequence('transfer_id_seq'),

        primary_key=True,

        server_default=Sequence('transfer_id_seq').next_value()

    )
    transaction_id = Column(Integer, ForeignKey("Transaction.transaction_id"), nullable=False)
    from_account_id_fk = Column(Integer, nullable=False)
    to_account_id_fk = Column(Integer, nullable=False)
    transfer_reference = Column(String(100))
    transfer_date = Column(Date, nullable=False)
    transaction = relationship("Transaction", back_populates="transfers")


class Check(Base):
    __tablename__ = "checks"
    checks_id = Column(
        Integer,
        Sequence('check_id_seq'),  # nom de la séquence
        primary_key=True,
        server_default=Sequence('checks_id_seq').next_value()
    )
    transaction_id = Column(Integer, ForeignKey("Transaction.transaction_id"), nullable=False)
    checks_number = Column(String(50))
    payee_name = Column(String(100))
    issue_date = Column(Date, nullable=False)
    clearance_date = Column(Date)
    transaction = relationship("Transaction", back_populates="checks")


# 4) (Optionnel) créer les tables en base
if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Tables créées.")
