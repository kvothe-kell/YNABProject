# Third-Party Imports
from dash import Output, Input
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# Local Application Imports
from data import database
from config import fetch_transactions, fetch_accounts

# Connect to the database
engine = create_engine(database.DATABASE_URI)


def register_callbacks(app):
    @app.callback(
        Output("account_dropdown", "options"),
        Input("account_dropdown", "id")  # Dummy input to trigger on page load
    )
    def populate_account_dropdown(_):
        accounts = fetch_accounts()
        options = [{"label": "All Accounts", "value": "all"}]

        if not accounts.empty:
            account_options = [{"label": row["account_name"], "value": row['account_id']} for _, row in
                               accounts.iterrows()]
            options.extend(account_options)
        return options

    @app.callback(
        Output("transaction-graph", "figure"),
        Input("transaction-graph", "id")  # Dummy input to trigger on page load
    )
    def update_transaction_graph(_):
        df = fetch_transactions()  # Use cached function instead of querying the DB directly

        if df is None or df.empty:
            return px.line(title="No Data Available")

        df = pd.read_sql("SELECT date, SUM(amount) as total FROM transactions GROUP BY date", engine)
        fig = px.line(df, x="date", y="total", title="Transaction Trends")
        return fig

    @app.callback(
        Output("summary-graph", "figure"),
        Input("account_dropdown", "value")
    )
    def update_summary_graph(selected_account):
        # Get all transactions (cached)
        transactions = fetch_transactions()

        if transactions is None or transactions.empty:
            return px.bar(title="No Data Available")

        # Filter by account if not "all"
        if selected_account and selected_account != "all":
            query = f'''
            SELECT category_name, SUM(amount) as total
            FROM transactions
            WHERE account_id = "{selected_account}"
            GROUP BY category_name
            ORDER By total DESC
            LIMIT 10
            '''
        else:
            query = '''
            SELECT category_name, SUM(amount) as total 
            FROM transactions 
            GROUP BY category_name 
            ORDER BY total DESC 
            LIMIT 10
            '''
        # Example: Get a summary of spending by category
        df_summary = pd.read_sql(query, engine)
        title = F"Top Spending Categories" + (
            f" for Selected Account" if selected_account and selected_account != "all" else "")
        fig = px.bar(df_summary, x="category_name", y="total", title=title)
        return fig
