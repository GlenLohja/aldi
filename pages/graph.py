import dash
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go

dash.register_page(__name__, name='Graphs')

# page 3 data

df2 = pd.read_excel('data/sample.xlsx', engine='openpyxl', sheet_name='Orders')

# Calculating 'Days to Ship'
df2['Days to Ship'] = (df2['Ship Date'] - df2['Order Date']).dt.days

# Filtering for the year 2016
df_2016 = df2[df2['Order Date'].dt.year == 2016]

# Grouping by year and week
grouped = df_2016.groupby([df_2016['Order Date'].dt.year, df_2016['Order Date'].dt.isocalendar().week])
# Grouping by year and month
# grouped = df_2016.groupby([df_2016['Order Date'].dt.year, df_2016['Order Date'].dt.month])
# Aggregate the required data
data = grouped.agg(
    Date=('Order Date', 'min'),  # Gets the first date of the week for labeling
    Days_to_Ship=('Days to Ship', 'mean'),
    Discount=('Discount', 'mean'),
    Profit=('Profit', 'sum'),
    Quantity=('Quantity', 'sum'),
    Sales=('Sales', 'sum')
).reset_index(drop=True)

data['Profit Ratio'] = data['Profit'] / data['Sales']
df = pd.DataFrame(data)

# Ensuring the 'Date' column reflects the correct start of each week
df['Date'] = df['Date'].dt.to_period('W').apply(lambda r: r.start_time)
df = df.sort_values(by='Date').reset_index(drop=True)
print(df['Date'])


    
df1 = pd.DataFrame({
    "Category": ["A", "B", "C", "D"],
    "Value": [10, 20, 30, 40],
    "Size": [100, 200, 300, 400]
})

fig = px.scatter(df1, x="Category", y="Value",
                 size="Size", color="Category",
                 size_max=60)

layout = html.Div(
    [   
        dbc.Row([
            dbc.Col([
                dbc.Label("Start Date"),
                dbc.Select(
                    id='country-dropdown',
                    options=[],
                    value=None,
                    placeholder="Start Date"
                )
            ], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2, align="center"),
            dbc.Col([
                dbc.Label("End Date"),
                dbc.Select(
                    id='state-dropdown',
                    options=[],
                    value=None,
                    placeholder="End Date"
                )
            ], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2, align="center"),
            dbc.Col([
                dbc.Label("Date Granularity"),
                dbc.Select(
                    id='city-dropdown',
                    options=[],
                    value=None,
                    placeholder="Granularity"
                )
            ], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2, align="center")
        ], style={'padding': '20px 0px'}),
        dbc.Row([
            dbc.Col(
                [   
                    html.Div([

                        dcc.Graph(
                        id='timeline-graph',
                            figure={
                                'data': [
                                    go.Scatter(x=df['Date'], y=df['Days_to_Ship'], name='Days to Ship', mode='lines', marker=dict(color='#2CA58D')),
                                    go.Scatter(x=df['Date'], y=df['Discount'], name='Discount', mode='lines', yaxis="y2", marker=dict(color='#B7C9F2')),
                                    go.Scatter(x=df['Date'], y=df['Profit'], name='Profit', mode='lines', yaxis="y3", marker=dict(color='#474F7A')),
                                    go.Scatter(x=df['Date'], y=df['Profit Ratio'], name='Profit Ratio', mode='lines', yaxis="y4", marker=dict(color='#81689D')),
                                    go.Scatter(x=df['Date'], y=df['Quantity'], name='Quantity', mode='lines', yaxis="y5", marker=dict(color='#FFD0EC')),
                                    # go.Scatter(x=df['Date'], y=df['Returns'], name='Returns', mode='lines'),
                                    go.Scatter(x=df['Date'], y=df['Sales'], name='Sales', mode='lines', yaxis="y6", marker=dict(color='#1F2544')),
                                ],
                                'layout': go.Layout(
                                    title='Timeline Graph',
                                    # xaxis=dict(title='Date'),
                                    yaxis=dict(
                                        title="Days to Ship",
                                        titlefont=dict(color="#2CA58D"),
                                        tickfont=dict(color="#2CA58D"),
                                    ),
                                    yaxis2=dict(
                                        title="Discount",
                                        overlaying="y",
                                        side="right",
                                        titlefont=dict(color="#B7C9F2"),
                                        tickfont=dict(color="#B7C9F2"),
                                    ),
                                    yaxis3=dict(title="Profit", anchor="free", overlaying="y", autoshift=True,titlefont=dict(color="#474F7A"),tickfont=dict(color="#474F7A")),
                                    yaxis4=dict(
                                        title="Profit Ratio",
                                        anchor="free",
                                        overlaying="y",
                                        side="right",
                                        autoshift=True,
                                        titlefont=dict(color="#81689D"),
                                        tickfont=dict(color="#81689D"),
                                    ),
                                    yaxis5=dict(title="Quantity", anchor="free", overlaying="y", autoshift=True, titlefont=dict(color="#FFD0EC"),tickfont=dict(color="#FFD0EC")),
                                    yaxis6=dict(title="Sales", anchor="free", overlaying="y", autoshift=True, titlefont=dict(color="#0A2342"),tickfont=dict(color="#0A2342")),
                                    legend=dict(bordercolor='rgba(255,255,255,0.5)', borderwidth=2, bgcolor='rgba(255,255,255,0.5)', orientation='h')  # Customize legend border
                                )
                            }
                        )
                    ], className="timeline-div")
                ], xs=12, sm=12, md=6, lg=6, xl=6, xxl=6,
            ),
            dbc.Col(
                [   
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("X Axis"),
                                dbc.Select(
                                    id='country-dropdown',
                                    options=[],
                                    value=None,
                                    placeholder="Sales"
                                ),
                            ], xs=4, sm=4, md=3, lg=3, xl=3, xxl=3, align="center"),
                            dbc.Col([
                                dbc.Label("Y Axis"),
                                dbc.Select(
                                    id='country-dropdown',
                                    options=[],
                                    value=None,
                                    placeholder="Profit"
                                ),
                            ], xs=4, sm=4, md=3, lg=3, xl=3, xxl=3, align="center"),
                            dbc.Col([
                                dbc.Label("Breakdown"),
                                dbc.Select(
                                    id='country-dropdown',
                                    options=[],
                                    value=None,
                                    placeholder="Category"
                                ),
                            ], xs=4, sm=4, md=3, lg=3, xl=3, xxl=3, align="center"),
                        ], style={'padding-top': '15px'}, justify="end"),
                        dcc.Graph(figure=fig)
                    ])
                ], className="bubble-chart-div", xs=12, sm=12, md=6, lg=6, xl=6, xxl=6
            )
        ]),
    ]
)