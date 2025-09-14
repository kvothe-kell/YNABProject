# Third-Party Imports
import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

import secrets_rs
from config import init_cache
from data import data_loader, database, ynab_calls

# Local Application Imports
# from pages import home, transactions  # Import pages

# Initialize the app with Dash
app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)
# app.title = "Financial Dashboard"

server = app.server  # Get the Flask server

# Initialize the cache
init_cache(app.server)

# Define Dash app layout
app.layout = html.Div(
    [
        # Simple navbar built from page registry
        html.Nav(
            [
                dcc.Link(p["name"], href=p["path"], style={"marginRight": 16})
                for p in dash.page_registry.values()
            ],
            style={"marginBottom": 24},
        ),
        dash.page_container,
    ]
)

# Register callbacks separately
from callbacks import net_worth, summary, transactions, waterfall

if __name__ == "__main__":
    # Import all data from YNAB
    budget_id = secrets_rs.BANANA_STAND_ID
    if budget_id:
        # Option 1: Sync everything
        # data_loader.sync_all_data(budget_id)

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
        app.run(debug=True)
