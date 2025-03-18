from dash import html, dcc

layout = html.Div([
    html.H1("Welcome to the Financial Dashboard"),
    dcc.Dropdown(
        id="account_dropdown",
        options=[],  # This will be populated dynamically
        placeholder="Select an Account",
        value="all"
    ),
    dcc.Graph(id="summary-graph")
])
