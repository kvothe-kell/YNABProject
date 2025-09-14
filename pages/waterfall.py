# Third-Party Imports
import dash
from dash import dcc, html

dash.register_page(__name__, path="/waterfall", name="Waterfall", order=3)

# Layout definition
# Includes an account dropdown, date range picker and graph placeholder
layout = html.Div(
    [
        html.H1("Balance Waterfall"),
        html.Div(
            [
                dcc.Dropdown(
                    id="wf-account-dropdown",
                    options=[],  # This will be populated dynamically
                    multi=True,
                    placeholder="Select Accounts",
                    value="all",
                    style={"width": "250px"},
                ),
                html.Div(
                    dcc.DatePickerRange(
                        id="wf-date-range",
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
        dcc.Graph(id="waterfall-graph"),
    ]
)
