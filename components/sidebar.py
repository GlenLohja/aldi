import dash_bootstrap_components as dbc
from dash import html


def create_sidebar():
    logo_url = "assets/Aldi_Süd_2017_logo.svg"
    return dbc.Nav(
        [
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Img(src=logo_url, height="75px", className="company-logo"),
                        html.H3("ALDI e", className="company")
                    ], className="page-header")
                ], width="auto", align="center")
            ], className="mb-4", align="center"),

            dbc.NavLink(
                html.Div([
                    html.I(className="fa-solid fa-house"),
                    html.Div("Home", className="ms-2"),
                ], className="d-flex align-items-center"),
                href="/",
                active="exact"
            ),
            dbc.NavLink(
                html.Div([
                    html.I(className="fa-solid fa-table"),
                    html.Div("Datatable", className="ms-2"),
                ], className="d-flex align-items-center"),
                href="/table",
                active="exact"
            ),
            dbc.NavLink(
                html.Div([
                    html.I(className="fa-solid fa-chart-line"),
                    html.Div("Graph", className="ms-2")
                ], className="d-flex align-items-center"),
                href="/graph",
                active="exact"
            )
        ],
        vertical=True,
        pills=True,
        className="bg-light"
    )
