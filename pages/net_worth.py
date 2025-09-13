# Third-Party Imports
import dash
from dash import dcc, html

dash.register_page(__name__, path="/net-worth", name="Net Worth", order=2)

layout = html.Div(
    [
        html.H1("Net Worth"),
        html.Div(
            [
                dcc.DatePickerRange(
                    id="nw_date_range",
                    display_format="MM/DD/YYYY",
                    start_date_placeholder_text="Start",
                    end_date_placeholder_text="End",
                    start_date=None,  # set by init callback
                    end_date=None,  # set by init callback
                ),
            ],
            style={
                "display": "flex",
                "gap": "10px",
                "alignItems": "center",
                "marginBottom": "12px",
            },
        ),
        dcc.Graph(id="net-worth-graph"),
    ]
)
