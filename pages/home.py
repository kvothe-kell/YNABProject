from dash import html, dcc

layout = html.Div([
    html.H1("Welcome to the Financial Dashboard"),
    dcc.Dropdown(
        id="account_dropdown",
        options=[],
        placeholder="Select an Account"
    ),
    dcc.Graph(id="summary-graph")
])
