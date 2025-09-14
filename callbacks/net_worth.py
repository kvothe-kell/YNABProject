import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback

from data.queries.net_worth import fetch_net_worth_date_range, fetch_net_worth_history


@callback(
    [Output("nw_date_range", "start_date"), Output("nw_date_range", "end_date")],
    Input("net-worth-graph", "id"),  # fires on first render
    prevent_initial_call=False,
)
def init_nw_bounds(_):
    min_d, max_d = fetch_net_worth_date_range()
    return min_d, max_d


@callback(
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
