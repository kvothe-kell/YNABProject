# Third-Party Imports
import pandas as pd
import plotly.express as px
from dash import Input, Output
from sqlalchemy import create_engine

from config import fetch_accounts, fetch_transactions

# Local Application Imports
from data import database

# Connect to the database
engine = create_engine(database.DATABASE_URI)


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
        base_query_select = """
            SELECT
                c.name AS category_name, 
                SUM(t.amount) as total
            FROM
                transactions t
            LEFT JOIN
                categories c ON t.category_id = c.id
        """
        group_order_limit = """
            GROUP BY
                c.name
            ORDER BY
                total DESC
            LIMIT 10
        """

        # if transactions is None or transactions.empty:
        #     return px.bar(title="No Data Available")

        if selected_account and selected_account != "all":
            query = f"""
            {base_query_select}
            WHERE
                t.account_id = "{selected_account}"
            {group_order_limit}
            """
        else:
            query = f"""
            {base_query_select}
            {group_order_limit}
            """
        df_summary = pd.read_sql(query, engine)

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

        fig = px.bar(df_summary, x="category_name", y="total", title=title)
        return fig
