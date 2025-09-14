# Third-Party Imports
import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
from sqlalchemy import create_engine

# Local Application Imports
from data import database

# Connect to the database
engine = create_engine(database.DATABASE_URI)


def get_transaction_data():
    query = "SELECT date, SUM(amount) as total FROM transactions GROUP BY date"
    return pd.read_sql(query, engine)


dash.register_page(__name__, path="/transactions", name="Transactions", order=4)

layout = html.Div([html.H1("Transactions"), dcc.Graph(id="transaction-graph")])
