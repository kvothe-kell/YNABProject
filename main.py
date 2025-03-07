import ynab
import secrets_rs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import String, Integer, Date, Boolean, ForeignKey, create_engine

# Database Setup
DATABASE_URL = "sqlite:///ynab_data.db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)


# Creates the Database with Explicit class definition
class Base(DeclarativeBase):
    pass


# Tables for creation in the database
class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[Date] = mapped_column(Date, index=True)
    amount: Mapped[int] = mapped_column(Integer)
    memo: Mapped[str | None] = mapped_column(String, nullable=True)
    cleared: Mapped[str] = mapped_column(String)
    approved: Mapped[bool] = mapped_column(Boolean)
    account_id: Mapped[str] = mapped_column(ForeignKey('accounts.id'))
    payee_id: Mapped[str | None] = mapped_column(String, nullable=True)
    category_id: Mapped[str | None] = mapped_column(String, nullable=True)
    account_name: Mapped[str] = mapped_column(String)
    payee_name: Mapped[str] = mapped_column(String)
    category_name: Mapped[str] = mapped_column(String)


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


# Initialize database (creates tables if they don't exist)
Base.metadata.create_all(engine)


class YNABClient:
    def __init__(self, access_token=None):
        """Initialize YNAB API Client."""
        self.configuration = ynab.Configuration(
            access_token=secrets_rs.ACCESS_TOKEN
        )

    def get_budgets(self):
        """Fetch the List of Budgets."""
        with ynab.ApiClient(self.configuration) as api_client:
            budgets_api = ynab.BudgetsApi(api_client)
            try:
                budgets_response = budgets_api.get_budgets()
                return budgets_response.data.budgets
            except Exception as e:
                print(f"Error fetching budgets: {e}")
                return []

    def get_transactions(self, budget_id):
        """Fetch transactions for a given budget ID"""
        with ynab.ApiClient(self.configuration) as api_client:
            transactions_api = ynab.TransactionsApi(api_client)
            try:
                transact_response = transactions_api.get_transactions(budget_id)
                return transact_response.data.transactions
            except Exception as e:
                print('Exception when calling TransactionsApi->get_transactions: %s\n' % e)
                return []

    def get_accounts(self, budget_id):
        """Fetch accounts for a given budegt ID."""
        with ynab.ApiClient(self.configuration) as api_client:
            accounts_api = ynab.AccountsApi(api_client)
            try:
                account_response = accounts_api.get_accounts(budget_id)
                return account_response.data.accounts  # List account objects
            except Exception as e:
                print(f"Error fetching accounts: {e}")
                return []


def store_transactions(transactions):
    session = SessionLocal()  # Create a new DB Session
    try:
        for txn in transactions:
            transactions_entry = Transaction(
                id=txn.id,
                date=txn.var_date,
                amount=txn.amount,
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
            session.add(transactions_entry)
        session.commit()
    except Exception as e:
        print(f"Error storing transactions: {e}")
        session.rollback()
    finally:
        session.close()  # Ensure session is always closed


if __name__ == "__main__":
    ynab_client = YNABClient()

    # Get all budgets
    budgets = ynab_client.get_budgets()
    for budget in budgets:
        print(f"Budget: {budget.name}")
    # Fetch transactions for a specific budget by name
    budget_id = secrets_rs.BANANA_STAND_ID
    if budget_id:
        transactions = ynab_client.get_transactions(budget_id)
        store_transactions(transactions)
        for transaction in transactions[:5]:  # Limit output for now
            print(f"Transaction: {transaction}")

    # Fetch accounts for thr budget
    if budget_id:
        accounts = ynab_client.get_accounts(budget_id)
        for account in accounts:
            print(f"Account: {account.name} (Balance: {account.balance})")

# yas
