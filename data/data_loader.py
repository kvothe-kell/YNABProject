# data_loader.py
from data.database import (
    SessionLocal, Transaction, Account, Category, Payee,
    SubTransaction, AccountBalanceHistory, Budget, MonthBudget
)
import datetime


def store_transactions(transactions):
    """Store transactions from YNAB API into the database"""
    session = SessionLocal()  # Create a new DB Session
    try:
        for txn in transactions:
            # handle subtransactions
            subtransactions_data = []
            if hasattr(txn, 'subtransactions') and txn.subtransactions:
                for sub_txn in txn.subtransactions:
                    subtransactions_data.append(SubTransaction(
                        id=sub_txn.id,
                        transaction_id=txn.id,
                        amount=sub_txn.amount / 1000,
                        memo=sub_txn.memo,
                        payee_id=sub_txn.payee_id,
                        category_id=sub_txn.category_id,
                        transfer_account_id=getattr(sub_txn, 'transfer_account_id', None),
                        deleted=getattr(sub_txn, 'deleted', False)
                    ))
            # Create Main Transaction
            transaction_entry = Transaction(
                id=txn.id,
                date=txn.var_date,
                amount=txn.amount / 1000,
                memo=txn.memo,
                cleared=txn.cleared,
                approved=txn.approved,
                account_id=txn.account_id,
                payee_id=txn.payee_id,
                category_id=txn.category_id
            )
            # Use merge for the main transaction (WTF IS THIS DOING)
            session.merge(transaction_entry)
            # For subtransactions check if they exist first
            for sub_entry in subtransactions_data:
                existing = session.query(SubTransaction).filter_by(id=sub_entry.id).first()
                if existing:
                    # Update existing transaction
                    for key, value in sub_entry.__dict__.items():
                        if key != '_sa_instance_state' and key != 'id':
                            setattr(existing, key, value)
                else:
                    session.add(sub_entry)

        session.commit()
    except Exception as e:
        print(f"Error storing transactions: {e}")
        session.rollback()
    finally:
        session.close()  # Ensure session is always closed


def store_categories(categories):
    """Store categories from YNAB API into the database"""
    session = SessionLocal()
    try:
        for category_group in categories:
            group_id = category_group.id
            group_name = category_group.name

            for cat in category_group.categories:
                category_entry = Category(
                    id=cat.id,
                    name=cat.name,
                    group_id=group_id,
                    group_name=group_name,
                    hidden=cat.hidden,
                    deleted=cat.deleted if hasattr(cat, 'deleted') else False
                )
                session.merge(category_entry)

        session.commit()
    except Exception as e:
        print(f"Error storing categories: {e}")
        session.rollback()
    finally:
        session.close()


def store_payees(payees):
    """Store payees from YNAB API into the database"""
    session = SessionLocal()
    try:
        for payee in payees:
            payee_entry = Payee(
                id=payee.id,
                name=payee.name,
                transfer_account_id=payee.transfer_account_id if hasattr(payee, 'transfer_account_id') else None,
                deleted=payee.deleted if hasattr(payee, 'deleted') else False
            )
            session.merge(payee_entry)
        session.commit()
    except Exception as e:
        print(f"Error storing payees: {e}")
        session.rollback()
    finally:
        session.close()


def store_accounts(accounts, session=None):
    """Store accounts from YNAB API into the database"""
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True
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

            # Also store current balance in history table
            store_account_balance_snapshot(acct, session=session)

        session.commit()
    except Exception as e:
        print(f"Error storing accounts: {e}")
        session.rollback()
    finally:
        if close_session:
            session.close()  # Ensure session is always closed


def store_account_balance_snapshot(account, snapshot_date=None, session=None):
    """Store current account balance in the history table"""
    if snapshot_date is None:
        snapshot_date = datetime.date.today()

    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True

    try:
        # Check if we already have a snapshot for this account/date
        existing = session.query(AccountBalanceHistory).filter_by(
            account_id=account.id,
            date=snapshot_date
        ).first()

        if existing:
            # Update existing Snapshot
            existing.balance = account.balance / 1000
            existing.cleared_balance = account.cleared_balance / 1000
            existing.uncleared_balance = account.uncleared_balance / 1000
        else:
            # Create new snapshot
            history_entry = AccountBalanceHistory(
                account_id=account.id,
                date=snapshot_date,
                balance=account.balance / 1000,
                cleared_balance=account.cleared_balance / 1000,
                uncleared_balance=account.uncleared_balance / 1000
            )
            session.add(history_entry)
        if close_session:
            session.commit()
    except Exception as e:
        print(f"Error storing account balance history: {e}")
        if close_session:
            session.rollback()
    finally:
        if close_session:
            session.close()


def store_budget(budget_data):
    """Store budget information from YNAB API"""  # NOT SUTE WHJAT THIS DEOSEITHER
    session = SessionLocal()
    try:
        # Store main budget info
        budget_entry = Budget(
            id=budget_data.id,
            name=budget_data.name,
            last_modified_on=budget_data.last_modified_on,
            first_month=budget_data.first_month,
            last_month=budget_data.last_month,
            currency_format=str(budget_data.currency_format) if hasattr(budget_data, 'currency_format') else None
        )
        session.merge(budget_entry)
        # Store month budget data if available
        if hasattr(budget_data, 'months') and budget_data.months:
            for month_data in budget_data.months:
                month_str = month_data.month

                # Process each category in the month
                if hasattr(month_data, 'categories') and month_data.categories:
                    for cat in month_data.categories:
                        month_budget_entry = MonthBudget(
                            budget_id=budget_data.id,
                            month=month_str,
                            category_id=cat.id,
                            budgeted=cat.budgeted / 1000,
                            activity=cat.activity / 1000,
                            balance=cat.balance / 1000
                        )

                        # Check if entry exists
                        existing = session.query(MonthBudget).filter_by(
                            budget_id=budget_data.id,
                            month=month_str,
                            category_id=cat.id
                        ).first()

                        if existing:
                            # Update existing entry
                            existing.budgeted = cat.budgeted / 1000
                            existing.activity = cat.activity / 1000
                            existing.balance = cat.balance / 1000
                        else:
                            # Add new entry
                            session.add(month_budget_entry)
        session.commit()
    except Exception as e:
        print(f"Error storing budget data: {e}")
    finally:
        session.close()


# def capture_month_end_balances():
#     """
#     Utility function to capture current account balances for historical tracking.
#     Ideal to run at month-end via a scheduled task.
#     """
#     from data.ynab_calls import YNABClient
#     import secrets_rs
#
#     ynab_client = YNABClient()
#     budget_id = secrets_rs.BANANA_STAND_ID
#
#     if budget_id:
#         # Get current date (or last day of previous month if running as scheduled task)
#         today = datetime.date.today()
#         if today.day == 1:  # If first day of month, use last day of previous month
#             # Move to previous day (last day of previous month)
#             snapshot_date = today - datetime.timedelta(days=1)
#         else:
#             snapshot_date = today
#
#         # Fetch current account data
#         accounts = ynab_client.get_accounts(budget_id)
#
#         # Store snapshots with the specific date
#         for account in accounts:
#             store_account_balance_snapshot(account, snapshot_date)
#
#         print(f"Captured balance snapshots for {len(accounts)} accounts as of {snapshot_date}")

def sync_all_data(budget_id):
    """
    Synchronize all data from YNAB API for a given budget.
    This is a comprehensive sync function that pulls all entity types.
    """
    from data.ynab_calls import YNABClient

    ynab_client = YNABClient()

    # Fetch and store budget info (includes months)
    budget_data = ynab_client.get_budget_by_id(budget_id)
    if budget_data:
        store_budget(budget_data)

    # Fetch and store categories
    categories = ynab_client.get_categories(budget_id)
    if categories:
        store_categories(categories)

    # Fetch and store payees
    payees = ynab_client.get_payees(budget_id)
    if payees:
        store_payees(payees)

    # Fetch and store accounts
    accounts = ynab_client.get_accounts(budget_id)
    if accounts:
        store_accounts(accounts)

    # Fetch and store transactions
    transactions = ynab_client.get_transactions(budget_id)
    if transactions:
        store_transactions(transactions)

    print(f"Completed full data sync for budget {budget_id}")
