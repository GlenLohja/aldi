import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.sidebar import create_sidebar

external_stylesheets = [
    'https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700;800;900&display=swap',
    dbc.themes.PULSE,
    dbc.icons.FONT_AWESOME
]

app = dash.Dash(__name__, use_pages=True, external_stylesheets=external_stylesheets)

server = app.server

sidebar = create_sidebar()

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