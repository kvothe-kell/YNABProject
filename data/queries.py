"""Database query helper functions with caching."""

import textwrap

import pandas as pd
from sqlalchemy import create_engine, text

from config import cache
from data import database

# Set up database engine
engine = create_engine(database.DATABASE_URI)


def fetch_summary(selected_account=None):
    """Return summary data for the given account.

    Results are cached for efficiency.
    """

    @cache.memoize(timeout=300)  # Cache results for 5 minutes
    def get_summary(account_id):
        base_query = textwrap.dedent(
            """
            SELECT
                c.name AS category_name,
                SUM(COALESCE(st.amount, t.amount)) AS total
            FROM
                transactions t
            LEFT JOIN
                subtransactions st ON st.transaction_id = t.id
            LEFT JOIN
                categories c ON COALESCE(st.category_id, t.category_id) = c.id
            WHERE
                c.name IS NOT NULL
                AND c.name NOT LIKE '%Ready to Assign%'
            """
        )

        group_order_limit = textwrap.dedent(
            """
            GROUP BY
                c.name
            ORDER BY
                ABS(total) DESC
            LIMIT 10
            """
        )

        if account_id and account_id != "all":
            query = textwrap.dedent(
                f"""
                {base_query}
                AND t.account_id = :account_id
                {group_order_limit}
                """
            )
            params = {"account_id": account_id}
        else:
            query = textwrap.dedent(
                f"""
                {base_query}
                {group_order_limit}
                """
            )
            params = {}

        df = pd.read_sql(text(query), engine, params=params)
        df["total"] = df["total"].abs()
        return df

    return get_summary(selected_account)
