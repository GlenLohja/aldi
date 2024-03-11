import dash_bootstrap_components as dbc
from dash import html

def create_card(icon_class, title, content):
    return dbc.Card(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.I(className=icon_class, style={"font-size": "3rem"}),
                        className="col-md-2 d-flex align-items-center justify-content-center",
                    ),
                    dbc.Col(
                        dbc.CardBody(
                            [
                                html.H4(title, className="card-title"),
                                html.P(content, className="card-text"),
                            ]
                        ),
                        className="col-md-10",
                    ),
                ],
                className="g-0 d-flex align-items-center",
            )
        ],
        className="mb-3",
        style={"maxWidth": "540px"},
    )