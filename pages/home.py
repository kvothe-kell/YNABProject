from dash import dcc, html

layout = html.Div(
    [
        html.H1("Welcome to the Financial Dashboard"),
        html.Div(
            [
                dcc.Dropdown(
                    id="account_dropdown",
                    options=[],  # This will be populated dynamically
                    placeholder="Select an Account",
                    value="all",
                    style={"width": "250px"},
                ),
                html.Div(
                    dcc.DatePickerRange(
                        id="date_range",
                        display_format="MM/DD/YYYY",
                        start_date_placeholder_text="Start Date",
                        end_date_placeholder_text="End Date",
                        start_date=None,
                        end_date=None,
                    ),
                    style={"marginLeft": "10px"},
                ),
            ],
            style={"display": "flex", "flexDirection": "row", "alignItems": "center"},
        ),
        dcc.Graph(id="summary-graph"),
    ]
)
