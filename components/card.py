import dash_bootstrap_components as dbc
from dash import html


def create_card(icon_class, title, content):
    return dbc.Card(
        [
            dbc.Row(
                [
                    dbc.Col([
                        html.I(className=icon_class, style={"fontSize": "3rem"}),
                    ], className="d-flex justify-content-end", xs=4, sm=4, md=4, lg=3, xl=3, xxl=2),
                    dbc.Col([
                        dbc.CardBody(
                            [
                                html.H4(title, className="card-title"),
                                html.P(content, className="card-text")
                            ]
                        ),
                    ], className="px-3", xs=8, sm=8, md=8, lg=9, xl=9, xxl=10)
                ],
                className="g-0 d-flex align-items-center"
            )
        ],
        className="mb-3"
    )
