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

if __name__ == "__main__":
    # Import all data from YNAB
    budget_id = secrets_rs.BANANA_STAND_ID
    if budget_id:
        # Option 1: Sync everything
        data_loader.sync_all_data(budget_id)

        # # Option 2: Or sync individual entities
        # ynab_client = ynab_calls.YNABClient()
        #
        # # Get and store categories
        # categories = ynab_client.get_categories(budget_id)
        # data_loader.store_categories(categories)
        #
        # # Get and store payees
        # payees = ynab_client.get_payees(budget_id)
        # data_loader.store_payees(payees)
        #
        # # Get and store accounts and their current balances
        # accounts = ynab_client.get_accounts(budget_id)
        # data_loader.store_accounts(accounts)
        #
        # # Get and store transactions
        # transactions = ynab_client.get_transactions(budget_id)
        # data_loader.store_transactions(transactions)
    app.run_server(debug=True)
