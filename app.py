import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700;800;900&display=swap',
    dbc.themes.PULSE,
    dbc.icons.FONT_AWESOME
]

app = dash.Dash(__name__, use_pages=True, external_stylesheets=external_stylesheets)

logo_url = "assets/Aldi_Süd_2017_logo.svg"

sidebar = dbc.Nav(
    [   
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Img(src=logo_url, height="75px", style={'display': 'inline-block', 'verticalAlign': 'middle'}),
                    html.H3("ALDI SÜD", className="company", style={'display': 'inline-block', 'verticalAlign': 'middle'}),
                ], style={'display': 'flex', 'alignItems': 'center'}),
            ], width="auto", align="center"),
        ], style={'margin-bottom': '25px'}, align="center"),


        dbc.NavLink(
            html.Div([
                html.I(className="fa-solid fa-house"),
                html.Div("Home", className="ms-2"),
            ], className="d-flex align-items-center"),
            href="/",
            active="exact",
        ),
        dbc.NavLink(
            html.Div([
                html.I(className="fa-solid fa-table"),
                html.Div("Datatable", className="ms-2"),
            ], className="d-flex align-items-center"),
            href="/table",
            active="exact",
        ),
        dbc.NavLink(
            html.Div([
                html.I(className="fa-solid fa-chart-line"),
                html.Div("Graph", className="ms-2"),
            ], className="d-flex align-items-center"),
            href="/graph",
            active="exact",
        ),
    ],
    vertical=True,
    pills=True,
    className="bg-light",
)

app.layout = dbc.Container([

    dbc.Row(
        [
            dbc.Col(
                [
                    sidebar
                ], xs=12, sm=12, md=2, lg=2, xl=2, xxl=2, style={'border-right': '0.1px solid #ecf0f4'}),

            dbc.Col(
                [
                    dash.page_container
                ], xs=12, sm=12, md=10, lg=10, xl=10, xxl=10, style={'margin-top':'60px'})
        ]
    )
], fluid=True)


if __name__ == "__main__":
    app.run(debug=True)