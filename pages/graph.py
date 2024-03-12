import dash
from dash import dcc, html, callback, Output, Input
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from datetime import date

dash.register_page(__name__, name='Graphs')


orders_df = pd.read_excel('data/sample.xlsx', engine='openpyxl', sheet_name='Orders')
returns_df = pd.read_excel('data/sample.xlsx', engine='openpyxl', sheet_name='Returns')

orders_df['Days to Ship'] = (orders_df['Ship Date'] - orders_df['Order Date']).dt.days
df_merged = pd.merge(orders_df, returns_df, on='Order ID', how='left')

# Pre-set start date and end date
start_date, end_date = '1/1/2017', '12/31/2017'

def filter_by_date(df, start_date, end_date):

    filtered_orders = df[(df['Order Date'] >= start_date) & (df['Order Date'] <= end_date)]
    return filtered_orders


def filter_by_granularity(df, granularity_option):

    if granularity_option == 'week':
        group_keys = [df['Order Date'].dt.year, df['Order Date'].dt.isocalendar().week]
    elif granularity_option == 'month':
        group_keys = [df['Order Date'].dt.year, df['Order Date'].dt.month]
    elif granularity_option == 'quarter':
        group_keys = [df['Order Date'].dt.year, df['Order Date'].dt.quarter]
    elif granularity_option == 'year':
        group_keys = [df['Order Date'].dt.year]
    else:
        return df



    grouped = df.groupby(group_keys).agg(
        Date=('Order Date', 'min'),
        Days_to_Ship=('Days to Ship', 'mean'),
        Discount=('Discount', 'mean'),
        Profit=('Profit', 'sum'),
        Quantity=('Quantity', 'sum'),
        Sales=('Sales', 'sum'),
        Ship_mode=('Ship Mode', 'count')
    )
    grouped['Profit Ratio'] = grouped['Profit'] / grouped['Sales']
    

    if granularity_option == 'week':
        grouped['Date'] = grouped['Date'].dt.to_period('W').dt.start_time
        grouped = grouped.sort_values(by='Date').reset_index(drop=True)

    return grouped


df_filtered_date = filter_by_date(df_merged, start_date, end_date)
df = filter_by_granularity(df_filtered_date, 'month')



def get_bubble_chart_data(df, yaxis, xaxis, category):

    grouped_df = df.groupby(category).agg({
        'Row ID': 'count',
        'Sales': 'sum',
        'Profit': 'sum',
        'Discount': 'mean',
        'Quantity': 'sum',
        'Days to Ship': 'mean',
        'Returned': lambda x: (x == 'Yes').sum()
    }).reset_index()

    grouped_df['Profit Ratio'] = grouped_df['Profit'] / grouped_df['Sales']

    if category != 'Product Name' and category != 'Sub-Category' and category != 'Category':
        unique_retuns = df.drop_duplicates(subset='Order ID').groupby(category).agg({
            'Returned': lambda x: (x == 'Yes').sum()
        }).reset_index()

        grouped_df['Returned'] = unique_retuns['Returned']
    
    return pd.DataFrame({
        xaxis: grouped_df[xaxis].tolist(),
        yaxis: grouped_df[yaxis].tolist(),
        f"{category} Count": grouped_df['Row ID'].tolist(),
        category: grouped_df[category].tolist(),
    })

df1 = get_bubble_chart_data(df_filtered_date, 'Sales', 'Profit', 'Ship Mode')


axis_options = [
    {'label': 'Days to Ship', 'value': 'Days to Ship'},
    {'label': 'Discount', 'value': 'Discount'},
    {'label': 'Profit', 'value': 'Profit'},
    {'label': 'Profit Ratio', 'value': 'Profit Ratio'},
    {'label': 'Quantity', 'value': 'Quantity'},
    {'label': 'Returns', 'value': 'Returned'},
    {'label': 'Sales', 'value': 'Sales'}
]

layout = html.Div(
    [   
        dbc.Row([
            dbc.Col([
                html.Div([
                    dbc.Label("Start Date")
                ]),
                html.Div([
                    dcc.DatePickerSingle(
                        id='start-date',
                        month_format='MMMM Y',
                        placeholder='MMMM Y',
                        date=date(2017, 1, 1)
                    )
                ])
            ], xs=12, sm=12, md=2, lg=2, xl=2, xxl=2),
            dbc.Col([   
                html.Div([
                    dbc.Label("End Date")
                ]),
                html.Div([
                    dcc.DatePickerSingle(
                        id='end-date',
                        month_format='MMMM Y',
                        placeholder='MMMM Y',
                        date=date(2017, 12, 31)
                    )
                ])
            ], xs=12, sm=12, md=2, lg=2, xl=2, xxl=2),
            dbc.Col([
                dbc.Label("Date Granularity"),
                dbc.Select(
                    id='granularity-dropdown',
                    options=[{'label' : 'Week', 'value': 'week'}, {'label' : 'Month', 'value': 'month'}, {'label' : 'Quarter', 'value': 'quarter'}, {'label' : 'Year', 'value': 'year'}],
                    value='month',
                    placeholder="Granularity"
                )
            ], xs=12, sm=12, md=2, lg=2, xl=2, xxl=2),
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
                                dbc.Label("Y Axis"),
                                dbc.Select(
                                    id='yaxis-dropdown',
                                    options=['Days to Ship', 'Discount', 'Profit Ratio', 'Quantity', 'Returns', 'Sales'],
                                    value='Sales',
                                ),
                            ], xs=4, sm=4, md=3, lg=3, xl=3, xxl=3, align="center"),
                            dbc.Col([
                                dbc.Label("X Axis"),
                                dbc.Select(
                                    id='xaxis-dropdown',
                                    options=['Days to Ship', 'Discount', 'Profit', 'Profit Ratio', 'Quantity', 'Returns'],
                                    value='Profit',
                                ),
                            ], xs=4, sm=4, md=3, lg=3, xl=3, xxl=3, align="center"),
                            dbc.Col([
                                dbc.Label("Breakdown"),
                                dbc.Select(
                                    id='breakdown-dropdown',
                                    options=['Segment', 'Ship Mode', 'Customer Name', 'Category', 'Sub-Category', 'Product Name'],
                                    value='Ship Mode',
                                    placeholder="Category"
                                ),
                            ], xs=4, sm=4, md=3, lg=3, xl=3, xxl=3, align="center"),
                        ], style={'padding-top': '15px'}, justify="end"),
                        dcc.Graph(
                            id='bubblechart',
                            figure={
                                'data': [
                                    go.Scatter(
                                        x=df1['Sales'], 
                                        y=df1['Profit'],
                                        mode='markers', 
                                        marker=dict(
                                            size=df1['Ship Mode Count'],
                                            # color=df1['Ship Mode'],
                                            sizeref= 2.*max(df1['Ship Mode Count'])/(15**2),
                                            sizemin=4,
                                        ),
                                        text=df1['Ship Mode Count'],
                                        hoverinfo='text'
                                    )
                                ],
                                'layout': go.Layout(
                                    xaxis=dict(title='Sales'),
                                    yaxis=dict(title='Profit'),
                                    margin=dict(l=100, r=20, t=70, b=70), # Adjust margins to fit your layout
                                    # height=600 # Adjust height if needed
                                )
                            }
                        )
                    ])
                ], className="bubble-chart-div", xs=12, sm=12, md=6, lg=6, xl=6, xxl=6
            )
        ]),
    ]
)

@callback(
    Output('yaxis-dropdown', 'options'),
    [Input('xaxis-dropdown', 'value')]
)
def set_yaxis_options(selected_xaxis):
    return [option for option in axis_options if option['value'] != selected_xaxis]

@callback(
    Output('xaxis-dropdown', 'options'),
    [Input('yaxis-dropdown', 'value')]
)
def set_xaxis_options(selected_yaxis):
    return [option for option in axis_options if option['value'] != selected_yaxis]


@callback(
    Output('bubblechart', 'figure'),
    [
        Input('xaxis-dropdown', 'value'),
        Input('yaxis-dropdown', 'value'),
        Input('breakdown-dropdown', 'value'),
        Input('start-date', 'date'),
        Input('end-date', 'date')
    ]
)
def update_bubble_chart(xaxis_val, yaxis_val, breakdown_val, start_date, end_date):

    filter_date = filter_by_date(df_merged, start_date, end_date)
    df_filtered =  get_bubble_chart_data(filter_date, xaxis_val, yaxis_val, breakdown_val)
    fig = {
        'data': [
            go.Scatter(
                x=df_filtered[xaxis_val],
                y=df_filtered[yaxis_val],
                mode='markers',
                marker=dict(
                    size=df_filtered[f'{breakdown_val} Count'],
                    sizeref=2.*max(df_filtered[f'{breakdown_val} Count'])/(15**2),
                    sizemin=4,
                ),
                text=df_filtered[f'{breakdown_val} Count'],
                hoverinfo='text'
            )
        ],
        'layout': go.Layout(
            xaxis=dict(title=xaxis_val),
            yaxis=dict(title=yaxis_val),
            margin=dict(l=100, r=20, t=70, b=70),
            # height=600
        )
    }
    return fig

@callback(
    Output('timeline-graph', 'figure'),
    [Input('start-date', 'date'),
    Input('end-date', 'date'),
    Input('granularity-dropdown', 'value')]
)
def update_timeline_chart(start_date, end_date, granularity):

    filter_date = filter_by_date(df_merged, start_date, end_date)
    updated_Df = filter_by_granularity(filter_date, granularity)

    figure={
        'data': [
            go.Scatter(x=updated_Df['Date'], y=updated_Df['Days_to_Ship'], name='Days to Ship', mode='lines', marker=dict(color='#2CA58D')),
            go.Scatter(x=updated_Df['Date'], y=updated_Df['Discount'], name='Discount', mode='lines', yaxis="y2", marker=dict(color='#B7C9F2')),
            go.Scatter(x=updated_Df['Date'], y=updated_Df['Profit'], name='Profit', mode='lines', yaxis="y3", marker=dict(color='#474F7A')),
            go.Scatter(x=updated_Df['Date'], y=updated_Df['Profit Ratio'], name='Profit Ratio', mode='lines', yaxis="y4", marker=dict(color='#81689D')),
            go.Scatter(x=updated_Df['Date'], y=updated_Df['Quantity'], name='Quantity', mode='lines', yaxis="y5", marker=dict(color='#FFD0EC')),
            # go.Scatter(x=df['Date'], y=df['Returns'], name='Returns', mode='lines'),
            go.Scatter(x=updated_Df['Date'], y=updated_Df['Sales'], name='Sales', mode='lines', yaxis="y6", marker=dict(color='#1F2544')),
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
    return figure