# Third-Party Imports
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Local Application Imports
from pages import home, transactions  # Import pages
from components import navbar  # Import navbar
from data import database, ynab_calls, data_loader
from callbacks import register_callbacks  # Import callbacks
from config import init_cache
import secrets_rs

# Initialize the app with Dash
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "Financial Dashboard"

server = app.server  # Get the Flask server

# Initialize the cache
init_cache(app.server)

# Define Dash app layout
app.layout = html.Div([
    navbar.create_navbar(),  # Navbar at the top
    dcc.Location(id="url", refresh=False),  # Tracks page changes
    html.Div(id="page-content")  # Page content updates dynamically
])


# Handle page routing
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == "/transactions":
        return transactions.layout
    else:
        return home.layout


# Register callbacks separately
register_callbacks(app)

# def update_graphs(_): NOT USED ANYMORE
#     # Query data from the Database
#     df1 = pd.read_sql("SELECT date, SUM(amount) as total FROM transactions GROUP BY date", database.engine)
#     df2 = pd.read_sql("SELECT category_name, SUM(amount) as total FROM transactions GROUP BY category_name",
#                       database.engine)
#
#     # Create figures
#     fig1 = px.line(df1, x="date", y="total", title="Total Amount Over Time")
#     fig2 = px.bar(df2, x="category_name", y="total", title="Spending by Category")
#
#     return fig1, fig2


if __name__ == "__main__":
    ynab_client = ynab_calls.YNABClient()

    # Get all budgets
    budgets = ynab_client.get_budgets()

    # Fetch transactions for a specific budget by name
    budget_id = secrets_rs.BANANA_STAND_ID
    if budget_id:
        ynab_transactions = ynab_client.get_transactions(budget_id)
        data_loader.store_transactions(ynab_transactions)

    # Fetch accounts for the budget
    if budget_id:
        ynab_accounts = ynab_client.get_accounts(budget_id)
        data_loader.store_accounts(ynab_accounts)
    # Run Dash App
    app.run_server(debug=True)
