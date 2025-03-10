from dash import html, dcc
import dash_bootstrap_components as dbc


def create_navbar():
    return dbc.NavbarSimple(
        children=[
            dbc.NavItem(dcc.Link("Home", href="/", className="nav-link")),
            dbc.NavItem(dcc.Link("Transactions", href="/transactions", className="nav-link"))
        ],
        brand="My Dashboard",
        color="dark",
        dark=True
    )
