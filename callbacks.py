# Third-Party Imports
import pandas as pd
import plotly.express as px
from dash import Input, Output

from config import fetch_accounts, fetch_transactions
from data.queries import fetch_summary


def register_callbacks(app):
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

    @app.callback(Output("summary-graph", "figure"), Input("account_dropdown", "value"))
    def update_summary_graph(selected_account):
        df_summary = fetch_summary(selected_account)

        if df_summary.empty:
            title = "No Data for Summary Graph"
            if selected_account and selected_account != "all":
                # You might want to fetch account name to make title more specific
                title += f" for Selected Account"
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
