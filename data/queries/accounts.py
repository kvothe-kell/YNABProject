import pandas as pd

from . import engine


def fetch_account_balance_on_date(target_date, account_ids=None):
    """Return balances for specific accounts on or before the target date"""
    if not target_date:
        return pd.DataFrame(columns=["account_id", "balance"])

    df = pd.read_sql(
        "SELECT account_id, date, balance FROM account_balance_history", engine
    )
    if df.empty:
        return df

    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] <= pd.to_datetime(target_date)]
    if account_ids:
        df = df[df["account_id"].isin(account_ids)]
    df = df.sort_values(["account_id", "date"]).groupby("account_id").tail(1)
    return df[["account_id", "balance"]]
