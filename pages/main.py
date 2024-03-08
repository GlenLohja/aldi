import dash
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import numpy as np

dash.register_page(__name__, path='/', name='Home')

df = pd.read_excel('data/sample.xlsx', engine='openpyxl', sheet_name='Orders')

df = {
    'Order Date': pd.date_range(start='2021-01-01', periods=4, freq='ME'),
    'Sales': [200, 400, 150, 600],
    'Profit': [100, 150, -50, 200],
    'Profit Ratio': [0.5, 0.375, -0.33, 0.33]
}

data = {
    'Product': ['Product A', 'Product B', 'Product C', 'Product D'],
    'Value': [1000, 1500, 1200, 1800]
}

# Generate sample data for 31 days for two months
np.random.seed(0)
days = pd.date_range(start='2022-01-01', periods=31)
profit_ratio_prev_month = np.random.uniform(low=0.1, high=0.8, size=31)  # Generating random profit ratios for previous month
profit_ratio_curr_month = np.random.uniform(low=0.1, high=0.8, size=31)  # Generating random profit ratios for current month

# Create DataFrame
df_prev_month = pd.DataFrame({'Date': days, 'Profit Ratio': profit_ratio_prev_month})
df_curr_month = pd.DataFrame({'Date': days, 'Profit Ratio': profit_ratio_curr_month})



card = dbc.Card(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.I(className="fa-solid fa-money-check-dollar", style={"font-size": "3rem"}),
                    className="col-md-2 d-flex align-items-center justify-content-center",
                ),
                dbc.Col(
                    dbc.CardBody(
                        [
                            html.H4("Total Sales", className="card-title"),
                            html.P(
                                "Glen.",
                                className="card-text",
                            ),
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
card2 = dbc.Card(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.I(className="fa-solid fa-money-bill-trend-up", style={"font-size": "3rem"}),
                    className="col-md-2 d-flex align-items-center justify-content-center",
                ),
                dbc.Col(
                    dbc.CardBody(
                        [   
                            html.H4("Total Profit", className="card-title"),
                            html.P(
                                "3400$",
                                className="card-text",
                            ),
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
card3 = dbc.Card(
    [
        dbc.Row(
            [
                dbc.Col(
                    html.I(className="fa-solid fa-percent", style={"font-size": "3rem"}),
                    className="col-md-2 d-flex align-items-center justify-content-center",
                ),
                dbc.Col(
                    dbc.CardBody(
                        [   
                            html.H4("Profit Ratio", className="card-title"),
                            html.P(
                                "52%",
                                className="card-text",
                            ),
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

layout = html.Div([
    dbc.Row([
        dbc.Col([
            card
        ], xs=6, sm=6, md=4, lg=4, xl=4, xxl=4, align="center"),
        dbc.Col([
            card2
        ], xs=6, sm=6, md=4, lg=4, xl=4, xxl=4, align="center"),
        dbc.Col([
            card3
        ], xs=6, sm=6, md=4, lg=4, xl=4, xxl=4, align="center"),
    ], style={'padding': '10px 0px'}),

    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='combo-chart',
                figure={
                    'data': [
                        go.Bar(
                            x=df['Order Date'],
                            y=df['Sales'] ,
                            name='Sales',
                            marker=dict(color='#427D9D') 
                        ),
                        go.Bar(
                            x=df['Order Date'],
                            y=df['Profit'] ,
                            name='Profit',
                            marker=dict(color='#9BBEC8') 
                        ),
                        go.Scatter(
                            x=df['Order Date'],
                            y=df['Profit Ratio'] ,
                            yaxis='y2',
                            mode='lines+markers',
                            name='Profit Ratio',
                            line=dict(color='#164863')
                        )
                    ],
                    'layout': go.Layout(
                        title='Sales, Profit, and Profit Ratio Over Time',
                        xaxis=dict(title='Date'),
                        yaxis=dict(title='Amount', side='left', rangemode='tozero'),
                        yaxis2=dict(title='Ratio %', side='right', overlaying='y', rangemode='tozero', tickformat='.0%'),
                        barmode='group',
                        legend=dict(bordercolor='rgba(255,255,255,0.5)', borderwidth=2, bgcolor='rgba(255,255,255,0.5)', orientation='h')  # Customize legend border
                    )
                }
            )
        ], xs=12, sm=6, md=8, lg=8, xl=8, xxl=8, align="center"),
        dbc.Col([
            dcc.Graph(
                id='horizontal-bar-chart',
                figure={
                    'data': [
                        go.Bar(
                            x=data['Value'],
                            y=data['Product'],
                            orientation='h',
                            marker=dict(color='#427D9D')
                        )
                    ],
                    'layout': go.Layout(
                        title='Product Value',
                        xaxis=dict(title='Value'),
                        yaxis=dict(title='Product'),
                        margin=dict(l=150),
                        height=400
                    )
                }
            )
        ], xs=12, sm=6, md=4, lg=4, xl=4, xxl=4, align="center")
    ], style={'padding': '10px 0px'}),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='timeline-chart',
                figure={
                    'data': [
                        go.Scatter(
                            x=df_prev_month['Date'],
                            y=df_prev_month['Profit Ratio'],
                            mode='lines+markers',
                            marker=dict(color='#B5C0D0'),
                            name='Previous week'
                        ),
                        go.Scatter(
                            x=df_curr_month['Date'],
                            y=df_curr_month['Profit Ratio'],
                            mode='lines+markers',
                            marker=dict(color='#40679E'),
                            name='Current Week'
                        )
                    ],
                    'layout': go.Layout(
                        title='Profit Ratio Timeline',
                        xaxis=dict(title='Date'),
                        yaxis=dict(title='Profit Ratio'),
                        hovermode='x'
                    )
                }
            )
        ], xs=12, sm=6, md=4, lg=4, xl=4, xxl=8, align="center"),
        dbc.Col([
            dcc.Graph(
                id='timeline-chart',
                figure={
                    'data': [
                        go.Scatter(
                            x=df_curr_month['Date'],
                            y=df_curr_month['Profit Ratio'],
                            mode='lines',
                            marker=dict(color='#40679E'),
                            name='Past 30 Days'
                        )
                    ],
                    'layout': go.Layout(
                        title='Number Of Oders Timeline',
                        xaxis=dict(title='Date'),
                        yaxis=dict(title='Orders'),
                        hovermode='x'
                    )
                }
            )
        ], xs=12, sm=6, md=4, lg=4, xl=4, xxl=4, align="center"),
        

    ], style={'padding': '10px 0px'}),
])



# @callback(
#     Output('line-fig', 'figure'),
#     Input('cont-choice', 'value')
# )
# def update_graph(value):
#     if value is None:
#         fig = px.histogram(df, x='continent', y='lifeExp', histfunc='avg')
#     else:
#         dff = df[df.continent==value]
#         fig = px.histogram(dff, x='country', y='lifeExp', histfunc='avg')
#     return fig