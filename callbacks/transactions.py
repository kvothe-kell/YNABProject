import pandas as pd
import plotly.express as px
from dash import Input, Output, callback

from config import fetch_transactions


# Create and update transactions graph
@callback(
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
    df_grouped = df_grouped.rename(columns={"amount": "total"}).sort_values(by="date")

    if df_grouped.empty:
        return px.line(title="No Transaction Data to Display Trends")

    fig = px.line(df_grouped, x="date", y="total", title="Transaction Trends")
    return fig
