from dash import Output, Input
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from data import database

# Connect to the database
engine = create_engine(database.DATABASE_URI)


def register_callbacks(app):
    @app.callback(
        Output("transaction-graph", "figure"),
        Input("transaction-graph", "id")  # Dummy input to trigger on page load
    )
    def update_transaction_graph(_):
        df = pd.read_sql("SELECT date, SUM(amount) as total FROM transactions GROUP BY date", engine)
        fig = px.line(df, x="date", y="total", title="Transaction Trends")
        return fig

    # New callback for home page
    @app.callback(
        Output("summary-graph", "figure"),
        Input("summary-graph", "id")
    )
    def update_summary_graph(_):
        # Example: Get a summary of spending by category
        df = pd.read_sql(
            "SELECT category_name, SUM(amount) as total FROM transactions GROUP BY category_name ORDER BY total DESC LIMIT 10",
            engine
        )
        fig = px.bar(df, x="category_name", y="total", title="Top Spending Categories")
        return fig
