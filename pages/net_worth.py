# Third-Party Imports
import dash
from dash import dcc, html

dash.register_page(__name__, path="/net-worth", name="Net Worth", order=0)

layout = html.Div([html.H1("Net Worth"), dcc.Graph(id="net-worth-graph")])
