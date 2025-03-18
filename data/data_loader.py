# data_loader.py
from data.database import SessionLocal, Transaction, Account


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


def store_accounts(accounts):  # I THINK THIS IS OK
    session = SessionLocal()  # Create a new DB Session
    try:
        for acct in accounts:
            account_entry = Account(
                id=acct.id,
                name=acct.name,
                type=acct.type,
                on_budget=acct.on_budget,
                closed=acct.closed,
                note=acct.note,
                balance=acct.balance / 1000,
                cleared_balance=acct.cleared_balance / 1000,
                uncleared_balance=acct.uncleared_balance / 1000,
                transfer_payee_id=acct.transfer_payee_id,
                direct_import_linked=acct.direct_import_linked,
                direct_import_in_error=acct.direct_import_in_error,
                deleted=acct.deleted
            )
            session.merge(account_entry)
        session.commit()
    except Exception as e:
        print(f"Error storing accounts: {e}")
        session.rollback()
    finally:
        session.close()  # Ensure session is always closed
