from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship
from sqlalchemy import String, Integer, Date, Boolean, ForeignKey, create_engine, UniqueConstraint, DateTime, Index
import datetime

# Database Setup
DATABASE_URI = "sqlite:///data/ynab_data.db"
engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)


# Create the Database with Explicit class definition
class Base(DeclarativeBase):
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow
    )


# Transaction data classes
class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    date: Mapped[Date] = mapped_column(Date, index=True)
    amount: Mapped[int] = mapped_column(Integer)
    memo: Mapped[str | None] = mapped_column(String, nullable=True)
    cleared: Mapped[str] = mapped_column(String)
    approved: Mapped[bool] = mapped_column(Boolean)
    account_id: Mapped[str] = mapped_column(ForeignKey('accounts.id'))
    payee_id: Mapped[str | None] = mapped_column(ForeignKey('payees.id'), nullable=True)
    category_id: Mapped[str | None] = mapped_column(ForeignKey('categories.id'), nullable=True)

    account = relationship("Account", back_populates="transactions")
    payee = relationship("Payee", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")
    subtransactions = relationship("SubTransaction", back_populates="transaction")

    __table_args__ = (
        # Most common query pattern: transactions by date range for a specific account
        Index('ix_transactions_date_account', 'date', 'account_id'),
        # For filtering by category (budget reporting)
        Index('ix_transactions_category_date', 'category_id', 'date'),
        # For filtering by payee
        Index('ix_transactions_payee_date', 'payee_id', 'date'),
    )


class SubTransaction(Base):
    __tablename__ = "subtransactions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    transaction_id: Mapped[str] = mapped_column(ForeignKey('transactions.id'))
    amount: Mapped[int] = mapped_column(Integer)
    memo: Mapped[str | None] = mapped_column(String, nullable=True)
    payee_id: Mapped[str | None] = mapped_column(ForeignKey('payees.id'), nullable=True)
    category_id: Mapped[str | None] = mapped_column(ForeignKey('categories.id'), nullable=True)
    transfer_account_id: Mapped[str | None] = mapped_column(String, nullable=True)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    transaction = relationship("Transaction", back_populates="subtransactions")

    __table_args__ = (
        # For retrieving all split parts of a transaction
        Index('ix_subtransactions_transaction', 'transaction_id'),
    )


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    group_id: Mapped[str | None] = mapped_column(String, nullable=True)
    group_name: Mapped[str | None] = mapped_column(String, nullable=True)
    hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    transactions = relationship("Transaction", back_populates="category")

    __table_args__ = (
        # For filtering categories by group
        Index('ix_categories_group', 'group_id'),
        # For searching categories by name
        Index('ix_categories_name', 'name'),
        # For filtering out hidden/deleted categories
        Index('ix_categories_hidden_deleted', 'hidden', 'deleted'),
    )


class Payee(Base):
    __tablename__ = "payees"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    transfer_account_id: Mapped[str | None] = mapped_column(String, nullable=True)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    transactions = relationship("Transaction", back_populates="payee")

    __table_args__ = (
        # For searching payees by name
        Index('ix_payees_name', 'name'),
        # For finding transfer payees
        Index('ix_payees_transfer_account', 'transfer_account_id'),
        # For filtering deleted payees
        Index('ix_payees_deleted', 'deleted'),
    )


# Account Data Classes
class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    on_budget: Mapped[bool] = mapped_column(Boolean)
    closed: Mapped[bool] = mapped_column(Boolean)
    note: Mapped[str] = mapped_column(String, nullable=True)
    balance: Mapped[int] = mapped_column(Integer)
    cleared_balance: Mapped[int] = mapped_column(Integer)
    uncleared_balance: Mapped[int] = mapped_column(Integer)
    transfer_payee_id: Mapped[str | None] = mapped_column(String, nullable=True)  # foreign key?
    direct_import_linked: Mapped[bool] = mapped_column(Boolean)
    direct_import_in_error: Mapped[bool] = mapped_column(Boolean)
    deleted: Mapped[bool] = mapped_column(Boolean)

    transactions = relationship("Transaction", back_populates="account")
    balance_history = relationship("AccountBalanceHistory", back_populates="account")

    __table_args__ = (
        # For filtering accounts by type
        Index('ix_accounts_type', 'type'),
        # For searching accounts by name
        Index('ix_accounts_name', 'name'),
        # For filtering on-budget accounts
        Index('ix_accounts_on_budget', 'on_budget'),
    )


class AccountBalanceHistory(Base):
    __tablename__ = "account_balance_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id: Mapped[str] = mapped_column(ForeignKey('accounts.id'))
    date: Mapped[Date] = mapped_column(Date, index=True)
    balance: Mapped[int] = mapped_column(Integer)
    cleared_balance: Mapped[int] = mapped_column(Integer)
    uncleared_balance: Mapped[int] = mapped_column(Integer)

    account = relationship("Account", back_populates="balance_history")

    # Add composite unique constraint
    __table_args__ = (UniqueConstraint('account_id', 'date', name='_account_date_uc'),)


# Budget data classes
class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    last_modified_on: Mapped[datetime.datetime] = mapped_column(DateTime)
    first_month: Mapped[str] = mapped_column(String)  # Format: YYYY-MM
    last_month: Mapped[str] = mapped_column(String)  # Format: YYYY-MM
    currency_format: Mapped[str | None] = mapped_column(String, nullable=True)

    month_budgets = relationship("MonthBudget", back_populates="budget")


class MonthBudget(Base):
    __tablename__ = "month_budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    budget_id: Mapped[str] = mapped_column(ForeignKey('budgets.id'))
    month: Mapped[str] = mapped_column(String)  # Format: YYYY-MM
    category_id: Mapped[str] = mapped_column(ForeignKey('categories.id'))
    budgeted: Mapped[int] = mapped_column(Integer)
    activity: Mapped[int] = mapped_column(Integer)
    balance: Mapped[int] = mapped_column(Integer)

    budget = relationship("Budget", back_populates="month_budgets")
    category = relationship("Category")

    __table_args__ = (
        # For retrieving a complete month's budget
        Index('ix_month_budgets_budget_month', 'budget_id', 'month'),
        # For category trend analysis over time
        Index('ix_month_budgets_category_month', 'category_id', 'month'),
        # For finding categories with specific budget characteristics
        Index('ix_month_budgets_budgeted', 'budgeted'),
        Index('ix_month_budgets_activity', 'activity'),
    )


# Initialize database (creates tables if they don't exist)


Base.metadata.create_all(engine)
