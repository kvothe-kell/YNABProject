import textwrap

import pandas as pd
from sqlalchemy import text

from . import cache, engine


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
