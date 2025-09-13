"""Database query helper functions with caching."""

import textwrap

import pandas as pd
from sqlalchemy import create_engine, text

from config import cache
from data import database

engine = create_engine(database.DATABASE_URI)


@cache.memoize(timeout=300)
def _get_txn_bounds():
    df = pd.read_sql(
        text("SELECT MIN(date) AS min_date, MAX(date) AS max_date FROM transactions"),
        engine,
    )
    if df.empty:
        return None, None
    min_d = (
        pd.to_datetime(df.loc[0, "min_date"]).date().isoformat()
        if pd.notna(df.loc[0, "min_date"])
        else None
    )
    max_d = (
        pd.to_datetime(df.loc[0, "max_date"]).date().isoformat()
        if pd.notna(df.loc[0, "max_date"])
        else None
    )
    return min_d, max_d


def fetch_transaction_date_range():
    """Return (min_date, max_date) as ISO strings. Call this from a callback."""
    return _get_txn_bounds()


def fetch_summary(selected_account=None, start_date=None, end_date=None):
    """Return summary data for the given account and date range (cached)."""

    @cache.memoize(timeout=300)
    def get_summary(account_id, start_date, end_date):
        base_query = textwrap.dedent(
            """
            SELECT
                c.name AS category_name,
                SUM(COALESCE(st.amount, t.amount)) AS total
            FROM transactions t
            LEFT JOIN subtransactions st ON st.transaction_id = t.id
            LEFT JOIN categories c ON COALESCE(st.category_id, t.category_id) = c.id
            WHERE c.name IS NOT NULL
              AND c.name NOT LIKE '%Ready to Assign%'
        """
        )

        filters = ""
        params = {}
        if account_id and account_id != "all":
            filters += " AND t.account_id = :account_id"
            params["account_id"] = account_id
        if start_date and end_date:
            filters += " AND t.date BETWEEN :start_date AND :end_date"
            params.update({"start_date": start_date, "end_date": end_date})
        elif start_date:
            filters += " AND t.date >= :start_date"
            params["start_date"] = start_date
        elif end_date:
            filters += " AND t.date <= :end_date"
            params["end_date"] = end_date

        group_order_limit = textwrap.dedent(
            """
            GROUP BY c.name
            ORDER BY ABS(total) DESC
            LIMIT 10
        """
        )

        query = textwrap.dedent(
            f"""
            {base_query}
            {filters}
            {group_order_limit}
        """
        )
        df = pd.read_sql(text(query), engine, params=params)
        if not df.empty:
            df["total"] = df["total"].abs()
        return df

    return get_summary(selected_account, start_date, end_date)


@cache.memoize(timeout=300)
def _get_net_worth_bounds():
    df = pd.read_sql(
        text(
            "SELECT MIN(date) AS min_date, MAX(date) AS max_date FROM account_balance_history"
        ),
        engine,
    )
    if df.empty:
        return None, None
    min_d = (
        pd.to_datetime(df.loc[0, "min_date"])
        .date()
        .isoformat()  # converts SQL value into Python Date and then string
        if pd.notna(
            df.loc[0, "min_date"]
        )  # stops error from happnening if SQL data is NULL
        else None
    )
    max_d = (
        pd.to_datetime(df.loc[0, "max_date"])
        .date()
        .isoformat()  # the df.loc is a row selector, from row 0 to min date.
        if pd.notna(df.loc[0, "max_date"])
        else None
    )
    return min_d, max_d


def fetch_net_worth_date_range():
    return _get_net_worth_bounds()


def _get_net_worth_history(start_date, end_date):
    """Return monthly net worth data with positive, negative, and net balances."""
    dialect = engine.dialect.name  # 'sqlite', 'postgresql', etc.
    where_parts, params = [], {}
    if start_date:
        where_parts.append("date >= :start_date")
        params["start_date"] = start_date
    if end_date:
        where_parts.append("date <= :end_date")
        params["end_date"] = end_date

    where_sql = "WHERE " + " AND ".join(where_parts) if where_parts else ""

    if dialect == "sqlite":
        sql = text(
            f"""
            SELECT
                strftime('%Y-%m', date) AS month,
                SUM(CASE WHEN balance >= 0 THEN balance ELSE 0 END) AS positive_balances,
                SUM(CASE WHEN balance < 0 THEN balance ELSE 0 END) AS negative_balances
            FROM account_balance_history
                   {where_sql}
            GROUP BY month
            ORDER BY month
        """
        )
    else:
        # Postgres and others
        sql = text(
            f"""
            SELECT
                to_char(date_trunc('month', date), 'YYYY-MM') AS month,
                SUM(CASE WHEN balance >= 0 THEN balance ELSE 0 END) AS positive_balances,
                SUM(CASE WHEN balance < 0 THEN balance ELSE 0 END) AS negative_balances
            FROM account_balance_history
            {where_sql}
            GROUP BY 1
            ORDER BY 1
        """
        )

    df = pd.read_sql(sql, engine, params=params)
    if df.empty:
        return df

    # Ensure consistent ordering & types
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")
    df = df.sort_values("month").reset_index(drop=True)

    # Net worth = pos + neg (neg should already be <= 0)
    df["net_worth"] = df["positive_balances"] + df["negative_balances"]
    return df


def fetch_net_worth_history(start_date=None, end_date=None):
    return _get_net_worth_history(start_date, end_date)  # <-- CALL it
