import pandas as pd
import plotly.express as px
from dash import Input, Output, callback

from config import fetch_accounts
from data.queries.transactions import fetch_summary


@callback(Output("account_dropdown", "options"), Input("account_dropdown", "id"))
def populate_account_dropdown(_):  # Dummy input to trigger on page load
    accounts = fetch_accounts()
    options = [{"label": "All Accounts", "value": "all"}]

    if accounts is not None and not accounts.empty:
        active_accounts = accounts[accounts["deleted"] == False]
        sorted_accounts = active_accounts.sort_values("name")
        account_options = [
            {"label": row["name"], "value": row["id"]}
            for _, row in sorted_accounts.iterrows()
        ]
        options.extend(account_options)
    return options


# Create and update summary spending top 10 categories
@callback(
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
