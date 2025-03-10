# data_loader.py
from data.database import SessionLocal, Transaction


def store_transactions(transactions):
    session = SessionLocal()  # Create a new DB Session
    try:
        for txn in transactions:
            transactions_entry = Transaction(
                id=txn.id,
                date=txn.var_date,
                amount=txn.amount / 1000,
                memo=txn.memo,
                cleared=txn.cleared,
                approved=txn.approved,
                account_id=txn.account_id,
                payee_id=txn.payee_id,
                category_id=txn.category_id,
                account_name=txn.account_name,
                payee_name=txn.payee_name,
                category_name=txn.category_name
            )
            session.merge(transactions_entry)
        session.commit()
    except Exception as e:
        print(f"Error storing transactions: {e}")
        session.rollback()
    finally:
        session.close()  # Ensure session is always closed
