import dash_bootstrap_components as dbc
from dash import dcc, html


def create_navbar():
    """Create the application's top navigation bar.

    Returns:
        dbc.NavbarSimple: Navigation bar with links to main pages.
    """
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dcc.Link("Home", href="/", className="nav-link")),
            dbc.NavItem(
                dcc.Link("Transactions", href="/transactions", className="nav-link")
            ),
        ],
        brand="My Dashboard",
        color="dark",
        dark=True,
    )
