# Third-Party Imports
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output

from config import fetch_accounts, fetch_transactions
from data.queries import (
    fetch_account_balance_on_date,
    fetch_net_worth_date_range,
    fetch_net_worth_history,
    fetch_summary,
)


def register_callbacks(app):
    """Attach all Dash backs to the given application instance.
    Args:
        app (dash.Dash): Dash application to whcih callbacsk are registered.

    Returns:
        None
    """

    # Create Account filter list
    @app.callback(
        Output("account_dropdown", "options"),
        Input("account_dropdown", "id"),  # Dummy input to trigger on page load
    )
    def populate_account_dropdown(_):
        accounts = fetch_accounts()
        options = [{"label": "All Accounts", "value": "all"}]

        if accounts is not None and not accounts.empty:
            # Filter out Deleted Accounts
            active_accounts = accounts[accounts["deleted"] == False]

            # Sort accounts alphabetically by name
            sorted_accounts = active_accounts.sort_values("name")

            account_options = [
                {"label": row["name"], "value": row["id"]}
                for _, row in sorted_accounts.iterrows()
            ]
            options.extend(account_options)
        return options

    # Create and update summary spending top 10 categories
    @app.callback(
        Output("summary-graph", "figure"),
        [
            Input("account_dropdown", "value"),
            Input("date_range", "start_date"),
            Input("date_range", "end_date"),
        ],
    )
    def update_summary_graph(selected_account, start_date, end_date):
        start = pd.to_datetime(start_date).date() if start_date else None
        end = pd.to_datetime(end_date).date() if end_date else None
        df_summary = fetch_summary(selected_account, start, end)

        if df_summary.empty:
            title = "No Data for Summary Graph"
            if selected_account and selected_account != "all":
                # You might want to fetch account name to make title more specific
                title += " for Selected Account"
            return px.bar(title=title)

        title = "Top 10 Spending Categories"
        if selected_account and selected_account != "all":
            # Ideally, fetch account name from `accounts` table using `selected_account` ID
            # For now, just indicating a filter is active.
            title += " (Filtered by Account)"

        fig = px.bar(
            df_summary,
            x="category_name",
            y="total",
            labels={"total": "Total Amount", "category_name": "Category"},
            title=title,
        )
        return fig

    # Create and Update networth graph with filters
    @app.callback(
        [Output("nw_date_range", "start_date"), Output("nw_date_range", "end_date")],
        Input("net-worth-graph", "id"),  # fires on first render
        prevent_initial_call=False,
    )
    def init_nw_bounds(_):
        min_d, max_d = fetch_net_worth_date_range()
        return min_d, max_d

    # B) Redraw the graph whenever the picker changes
    @app.callback(
        Output("net-worth-graph", "figure"),
        [Input("nw_date_range", "start_date"), Input("nw_date_range", "end_date")],
    )
    def update_net_worth_graph(start_date, end_date):
        df_net = fetch_net_worth_history(start_date, end_date)
        if df_net is None:
            return px.bar(title="No Net Worth Data")

        df_net["month"] = pd.to_datetime(df_net["month"])

        fig = go.Figure()
        fig.add_bar(
            x=df_net["month"], y=df_net["positive_balances"], name="Positive Balances"
        )
        fig.add_bar(
            x=df_net["month"], y=df_net["negative_balances"], name="Negative Balances"
        )
        fig.add_trace(
            go.Scatter(
                x=df_net["month"],
                y=df_net["net_worth"],
                name="Net Worth",
                mode="lines+markers",
            )
        )
        fig.update_layout(
            barmode="relative",
            title="Net Worth Over Time",
            xaxis_title="Month",
            yaxis_title="Amount",
        )
        return fig

    @app.callback(
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
    @app.callback(
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

    # Create and update transactions graph
    @app.callback(
        Output("transaction-graph", "figure"),
        Input("transaction-graph", "id"),  # Dummy input to trigger on page load
    )
    def update_transaction_graph(_):
        df_all_transactions = fetch_transactions()  # get full cached DataFrame

        if df_all_transactions is None or df_all_transactions.empty:
            return px.line(title="No Data Available")

        # Ensure 'date' column in the datetime format for proper grouping/sorting
        df_all_transactions["date"] = pd.to_datetime(df_all_transactions["date"])

        # Perform grouping and sum with pandas
        df_grouped = df_all_transactions.groupby("date")["amount"].sum().reset_index()
        df_grouped = df_grouped.rename(columns={"amount": "total"}).sort_values(
            by="date"
        )

        if df_grouped.empty:
            return px.line(title="No Transaction Data to Display Trends")

        fig = px.line(df_grouped, x="date", y="total", title="Transaction Trends")
        return fig
