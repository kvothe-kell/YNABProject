from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import String, Integer, Date, Boolean, ForeignKey, create_engine

# Database Setup
DATABASE_URI = "sqlite:///data/ynab_data.db"
engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(bind=engine)


# Create the Database with Explicit class definition
class Base(DeclarativeBase):
    pass


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


class Account(Base):  # THIS NEEDS TO BE UPDATED
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


# Initialize database (creates tables if they don't exist)
Base.metadata.create_all(engine)
