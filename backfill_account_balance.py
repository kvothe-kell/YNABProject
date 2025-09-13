# """
# Backfill month-end account balances into `account_balance_history` from `transactions`.

# Assumptions:
# - `transactions` table has at least: id, date, account_id, amount
# - `accounts` table has at least: id, name, closed (bool-ish)
# - Amounts are in currency units (e.g., dollars). If they are in YNAB milliunits, pass --milliunits.

# Run:
#     python backfill_account_balance.py
# """

# import argparse
# import sys

# import pandas as pd
# from sqlalchemy import create_engine, text

# from data import database


# def _detect_milliunits(df_txn: pd.DataFrame) -> bool:
#     """If absolute median amount is >= 10,000 it's likely milliunits."""
#     if df_txn.empty:
#         return False
#     med = df_txn["amount"].abs().median()
#     return med >= 10000  # e.g., $20 -> 20000 mu


# def build_monthly_balances(
#     df_txn: pd.DataFrame, df_account: pd.DataFrame
# ) -> pd.DataFrame:
#     """Return DataFrame with columns [date (month-end), account_id, balance]."""
#     if df_txn.empty:
#         return pd.DataFrame(columns=["date", "account_id", "balance"])

#     df = df_txn.copy()
#     df["date"] = pd.to_datetime(df["date"])
#     # Ensure numeric amounts
#     df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

#     # Stable ordering within day (uses id if present)
#     order_cols = ["account_id", "date"] + (["id"] if "id" in df.columns else [])
#     df = df.sort_values(order_cols)

#     # Running balance per account
#     df["running_balance"] = df.groupby("account_id", group_keys=False)[
#         "amount"
#     ].cumsum()

#     # Month bucket and pick last txn per account per month
#     df["month"] = df["date"].values.astype("datetime64[M]")
#     idx = df.groupby(["account_id", "month"])["date"].idxmax()
#     month_end_rows = df.loc[idx, ["account_id", "date", "running_balance"]].copy()

#     # Use true month-end date for storage clarity
#     month_end_rows["date"] = (
#         month_end_rows["date"].dt.to_period("M").dt.to_timestamp("M")
#     )
#     month_end_rows = month_end_rows.rename(columns={"running_balance": "balance"})

#     out = month_end_rows[["date", "account_id", "balance"]].copy()
#     out = out.sort_values(["date", "account_id"]).reset_index(drop=True)
#     return out


# def write_account_balance_history(engine, df_hist: pd.DataFrame, if_exists="replace"):
#     """Persist to DB and add indexes."""
#     if df_hist.empty:
#         print(
#             "No data to write; account_balance_history will not be created.",
#             file=sys.stderr,
#         )
#         return

#     df = df_hist.copy()
#     df["date"] = pd.to_datetime(df["date"]).dt.date  # store as DATE
#     df.to_sql("account_balance_history", engine, if_exists=if_exists, index=False)

#     # Helpful indexes
#     with engine.begin() as conn:
#         try:
#             conn.execute(
#                 text(
#                     "CREATE INDEX IF NOT EXISTS idx_abh_date ON account_balance_history(date)"
#                 )
#             )
#         except Exception:
#             pass
#         try:
#             conn.execute(
#                 text(
#                     "CREATE INDEX IF NOT EXISTS idx_abh_acct ON account_balance_history(account_id)"
#                 )
#             )
#         except Exception:
#             pass


# def main():
#     parser = argparse.ArgumentParser(
#         description="Backfill month-end balances into account_balance_history."
#     )
#     parser.add_argument(
#         "--append",
#         action="store_true",
#         help="Append instead of replace (default is replace).",
#     )
#     parser.add_argument(
#         "--milliunits",
#         action="store_true",
#         help="Treat transaction amounts as YNAB milliunits.",
#     )
#     args = parser.parse_args()

#     engine = create_engine(database.DATABASE_URI)

#     # Load source tables
#     df_txn = pd.read_sql(text("SELECT * FROM transactions"), engine)
#     try:
#         df_acct = pd.read_sql(text("SELECT * FROM accounts"), engine)
#     except Exception:
#         df_acct = pd.DataFrame(columns=["id", "name", "closed"])

#     if df_txn.empty:
#         print("transactions table is empty: nothing to backfill.", file=sys.stderr)
#         sys.exit(0)

#     # Amount units
#     use_mu = args.milliunits or _detect_milliunits(df_txn)
#     if use_mu:
#         print(
#             "Detected milliunits (or --milliunits supplied). Converting amounts by / 1000."
#         )
#         df_txn["amount"] = df_txn["amount"] / 1000.0

#     # Build and persist
#     month_ends = build_monthly_balances(df_txn, df_acct)
#     if_exists = "append" if args.append else "replace"
#     write_account_balance_history(engine, month_ends, if_exists=if_exists)

#     print(
#         f"Wrote {len(month_ends):,} rows to account_balance_history (mode={if_exists})."
#     )


# if __name__ == "__main__":
#     main()
