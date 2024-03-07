import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.PULSE])

sidebar = dbc.Nav(
            [
                dbc.NavLink(
                    [
                        html.Div(page["name"], className="ms-2"),
                    ],
                    href=page["path"],
                    active="exact",
                )
                for page in dash.page_registry.values()
            ],
            vertical=True,
            pills=True,
            className="bg-light",
)

logo_url = "assets/Aldi_Süd_2017_logo.svg"
app.layout = dbc.Container([
    # dbc.Row([
    #     dbc.Col([
    #         
    #         html.Div([
    #             html.H2("ALDI SÜD", className="me-2", style={'display': 'inline-block', 'verticalAlign': 'middle'}),
    #             html.Img(src=logo_url, height="75px", style={'display': 'inline-block', 'verticalAlign': 'middle'}),
    #         ], style={'display': 'flex', 'alignItems': 'center'}),
    #         # This styles the Div to align items horizontally and center them vertically
    #     ], width="auto", align="center"),
    # ], style={'padding-top': '10px'}, align="center"),

    dbc.Row(
        [
            dbc.Col(
                [
                    sidebar
                ], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2),

            dbc.Col(
                [
                    dash.page_container
                ], xs=8, sm=8, md=10, lg=10, xl=10, xxl=10)
        ]
    )
], fluid=True)


if __name__ == "__main__":
    app.run(debug=True)