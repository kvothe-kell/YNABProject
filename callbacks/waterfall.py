import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback

from config import fetch_accounts, fetch_transactions
from data.queries.accounts import fetch_account_balance_on_date


@callback(
    Output("wf-account-dropdown", "options"),
    Input("wf-account-dropdown", "id"),
)
def populate_wf_account_dropdown(_):
    accounts = fetch_accounts()
    options = []

    if accounts is not None and not accounts.empty:
        active_accounts = accounts[accounts["deleted"] == False]
        sorted_accounts = active_accounts.sort_values("name")
        options = [
            {"label": row["name"], "value": row["id"]}
            for _, row in sorted_accounts.iterrows()
        ]
    return options


# Create and update Expenses Waterfall
@callback(
    Output("waterfall-graph", "figure"),
    [
        Input("wf-account-dropdown", "value"),
        Input("wf-date-range", "start_date"),
        Input("wf-date-range", "end_date"),
    ],
)
def update_waterfall_graph(selected_accounts, start_date, end_date):
    df_txn = fetch_transactions()

    if df_txn is None or df_txn.empty:
        return go.Figure()

    df_txn["date"] = pd.to_datetime(df_txn["date"])
    # filter down the dateframe to the date provided from the filters
    if selected_accounts:
        df_txn = df_txn[df_txn["account_id"].isin(selected_accounts)]
    if start_date:
        df_txn = df_txn[df_txn["date"] >= pd.to_datetime(start_date)]
    if end_date:
        df_txn = df_txn[df_txn["date"] <= pd.to_datetime(end_date)]
    # Sum positive and negative transactions
    income = df_txn[df_txn["amount"] > 0]["amount"].sum()
    expense = df_txn[df_txn["amount"] < 0]["amount"].sum()

    # Now collect starting and ending balances
    start_bal_df = fetch_account_balance_on_date(
        start_date, selected_accounts if selected_accounts != "all" else None
    )  # data frame query takes two arguments, target date and account ID
    start_balance = (
        start_bal_df["balance"].sum() if not start_bal_df.empty else 0
    )  # grabs balance from the dataframe added during the query
    end_balance = start_balance + income + expense

    # make the actual graph to display the information
    fig = go.Figure(
        go.Waterfall(
            measure=["absolute", "relative", "relative", "total"],
            x=[
                "Starting Balance",
                "Income",
                "Expenses",
                "Ending Balance",
            ],
            y=[start_balance, income, expense, end_balance],
        )
    )
    fig.update_layout(title="Balance Changes")
    return fig
