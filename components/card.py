import dash_bootstrap_components as dbc
from dash import html


def create_card(icon_class, title, content):
    return dbc.Card(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.I(className=icon_class, style={"fontSize": "3rem"}),
                        className="col-md-2 d-flex justify-content-end"
                    ),
                    dbc.Col(
                        dbc.CardBody(
                            [
                                html.H4(title, className="card-title"),
                                html.P(content, className="card-text")
                            ]
                        ),
                        className="col-md-10 px-3"
                    )
                ],
                className="g-0 d-flex align-items-center"
            )
        ],
        className="mb-3"
    )
