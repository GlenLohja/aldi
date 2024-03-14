import dash
from dash import dcc, html, callback, clientside_callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import date
from dash.exceptions import PreventUpdate


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
        Returned=('Returned', lambda x: (x == 'Yes').sum()),
        Ship_mode=('Ship Mode', 'count')
    )
    grouped['Profit Ratio'] = grouped['Profit'] / grouped['Sales']

    if granularity_option == 'week':
        grouped['Date'] = grouped['Date'].dt.to_period('W').dt.start_time
        grouped = grouped.sort_values(by='Date').reset_index(drop=True)

    return grouped


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

    grouped_df['Profit Ratio'] = (grouped_df['Profit'] / grouped_df['Sales']) * 100
    grouped_df['Discount'] = grouped_df['Discount'] * 100 

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
    if start_date is None or end_date is None or xaxis_val is None or yaxis_val is None or breakdown_val is None:
        raise PreventUpdate

    filter_date = filter_by_date(df_merged, start_date, end_date)
    df_filtered =  get_bubble_chart_data(filter_date, xaxis_val, yaxis_val, breakdown_val)

    # hover config
    x_format = '%{x:.0f}'
    if xaxis_val == 'Profit' or xaxis_val == 'Sales':
        x_format = '$%{x:,.0f}'
    elif xaxis_val == 'Profit Ratio' or xaxis_val == 'Discount':
        x_format = '%{x:.2f}%'

    y_format = '%{y:.0f}'
    if yaxis_val == 'Profit' or yaxis_val == 'Sales':
        y_format = '$%{y:,.0f}'
    elif yaxis_val == 'Profit Ratio' or yaxis_val == 'Discount':
        y_format = '%{y:.2f}%'

    fig = {
        'data': [
            go.Scatter(
                x=df_filtered[xaxis_val],
                y=df_filtered[yaxis_val],
                mode='markers',
                marker=dict(
                    size=df_filtered[f'{breakdown_val} Count'],
                    sizeref=2. * max(df_filtered.get(f'{breakdown_val} Count', []), default=0) / (15**2),
                    sizemin=4,
                ),
                text=df_filtered[f'{breakdown_val} Count'],
                customdata=df_filtered[breakdown_val],
                hovertemplate=f"<b>%{{customdata}}: %{{text}}</b><br><br>{xaxis_val}: {x_format}<br>{yaxis_val}: {y_format}<br>"
                
            )
        ],
        'layout': go.Layout(
            xaxis=dict(title=xaxis_val),
            yaxis=dict(title=yaxis_val),
            height=520
        )
    }
    return fig


@callback(
    Output('timeline-graph', 'figure'),
    [Input('start-date', 'date'),
    Input('end-date', 'date'),
    Input('granularity-dropdown', 'value')]
)
def update_timeline_chart_v2(start_date, end_date, granularity):
    if start_date is None or end_date is None or granularity is None:
        raise PreventUpdate

    filter_date = filter_by_date(df_merged, start_date, end_date)
    updated_df = filter_by_granularity(filter_date, granularity)
    
    mode = 'lines'
    if len(updated_df) == 1:
        mode += '+markers'

    hovertemplate = "<b>%{x}</b><br>%{y:.2f}"

    # Create a subplot figure with 2x2 grid
    fig = make_subplots(rows=2, cols=2, shared_xaxes=True, vertical_spacing=0.1, horizontal_spacing=0.25,)

    # Plot Profit and Sales as stacked bars on the primary y-axis of the first subplot
    fig.add_trace(go.Bar(x=updated_df['Date'], y=updated_df['Profit'], name='Profit', marker=dict(color='#e6221b'), hovertemplate=hovertemplate + " Profit</br>"), row=1, col=1)
    fig.add_trace(go.Bar(x=updated_df['Date'], y=updated_df['Sales'], name='Sales', marker=dict(color='#4c7a9c'), hovertemplate=hovertemplate + " Sales</br>"), row=1, col=1)

    # Plot Discount and Profit Ratio as lines on the secondary y-axis of the first subplot
    fig.add_trace(go.Scatter(x=updated_df['Date'], y=updated_df['Discount'], name='Discount', mode='lines', marker=dict(color='#e6221b'), hovertemplate=hovertemplate + " Discount</br>"), row=1, col=2)
    fig.add_trace(go.Scatter(x=updated_df['Date'], y=updated_df['Profit Ratio'], name='Profit Ratio', mode='lines', marker=dict(color='#4c7a9c'), hovertemplate=hovertemplate + " Profit Ratio</br>"), row=1, col=2)

    # Top right subplot with Discount
    fig.add_trace(go.Bar(x=updated_df['Date'], y=updated_df['Returned'], name='Returns', marker=dict(color='#e6221b'), hovertemplate=hovertemplate + " Returns</br>"), row=2, col=1)
    fig.add_trace(go.Bar(x=updated_df['Date'], y=updated_df['Quantity'], name='Quantity', marker=dict(color='#4c7a9c'), hovertemplate=hovertemplate + " Quantity</br>"), row=2, col=1)

    # Bottom right subplot with Quantity, Returns, and Sales
    fig.add_trace(go.Scatter(x=updated_df['Date'], y=updated_df['Days_to_Ship'], name='Days to Ship', mode='lines', marker=dict(color='#e6221b'), hovertemplate=hovertemplate + " Days to Ship</br>"), row=2, col=2)

    # Update layout for shared x-axis and distinct y-axis configurations
    fig.update_layout(height=600, title_text="Timeline Graph", plot_bgcolor='rgba(255,255,255,0.5)', legend=dict(bordercolor='rgba(255,255,255,0.5)', borderwidth=2, bgcolor='rgba(255,255,255,0.5)', orientation='h') )
    fig.update_yaxes(title_text="Profit & Sales", row=1, col=1)
    fig.update_yaxes(title_text="Discount & Profit Ratio", tickformat='.0%', row=1, col=2)
    fig.update_yaxes(title_text="Quantity & Returns", row=2, col=1)
    fig.update_yaxes(title_text="Days to ship", row=2, col=2)

    fig.update_xaxes(gridcolor='#EEEEEE')
    fig.update_yaxes(gridcolor='#EEEEEE')
    return fig

# version 1 
# @callback(
#     Output('timeline-graph', 'figure'),
#     [Input('start-date', 'date'),
#     Input('end-date', 'date'),
#     Input('granularity-dropdown', 'value')]
# )
# def update_timeline_chart(start_date, end_date, granularity):
#     if start_date is None or end_date is None or granularity is None:
#         raise PreventUpdate

#     filter_date = filter_by_date(df_merged, start_date, end_date)
#     updated_df = filter_by_granularity(filter_date, granularity)
    
#     mode = 'lines'
#     if len(updated_df) == 1:
#         mode += '+markers'

#     hovertemplate="<b>%{x}</b><br>%{y:.2f}"
#     figure={
#         'data': [
#             go.Scatter(x=updated_df['Date'], y=updated_df['Days_to_Ship'], name='Days to Ship', mode=mode, marker=dict(color='#2CA58D'), hovertemplate=hovertemplate + " Days to ship</br>"),
#             go.Scatter(x=updated_df['Date'], y=updated_df['Discount'], name='Discount', mode=mode, yaxis="y2", marker=dict(color='#B7C9F2'), hovertemplate=hovertemplate + " Discount</br>"),
#             go.Scatter(x=updated_df['Date'], y=updated_df['Profit'], name='Profit', mode=mode, yaxis="y3", marker=dict(color='#474F7A'), hovertemplate=hovertemplate + " Profit</br>"),
#             go.Scatter(x=updated_df['Date'], y=updated_df['Profit Ratio'], name='Profit Ratio', mode=mode, yaxis="y4", marker=dict(color='#81689D'), hovertemplate=hovertemplate + " Profit Ratio</br>"),
#             go.Scatter(x=updated_df['Date'], y=updated_df['Quantity'], name='Quantity', mode=mode, yaxis="y5", marker=dict(color='#FFD0EC'), hovertemplate=hovertemplate + " Quantity</br>"),
#             go.Scatter(x=updated_df['Date'], y=updated_df['Returned'], name='Returns', yaxis="y6", mode=mode, hovertemplate=hovertemplate + " Returns"),
#             go.Scatter(x=updated_df['Date'], y=updated_df['Sales'], name='Sales', mode=mode, yaxis="y7", marker=dict(color='#1F2544'), hovertemplate=hovertemplate + " Sales</br>"),
#         ],
#         'layout': go.Layout(
#             title='Timeline Graph',
#             yaxis=dict(
#                 title="Days to Ship",
#                 titlefont=dict(color="#2CA58D"),
#                 tickfont=dict(color="#2CA58D"),
#             ),
#             yaxis2=dict(
#                 title="Discount",
#                 overlaying="y",
#                 side="right",
#                 titlefont=dict(color="#B7C9F2"),
#                 tickfont=dict(color="#B7C9F2"),
#                 tickformat='.0%'
#             ),
#             yaxis3=dict(title="Profit", anchor="free", overlaying="y", autoshift=True, titlefont=dict(color="#474F7A"),tickfont=dict(color="#474F7A")),
#             yaxis4=dict(
#                 title="Profit Ratio",
#                 anchor="free",
#                 overlaying="y",
#                 side="right",
#                 autoshift=True,
#                 titlefont=dict(color="#81689D"),
#                 tickfont=dict(color="#81689D"),
#                 tickformat='.0%'
#             ),
#             yaxis5=dict(title="Quantity", anchor="free", overlaying="y", autoshift=True, titlefont=dict(color="#FFD0EC"),tickfont=dict(color="#FFD0EC")),
#             yaxis6=dict(title="Returns", anchor="free", overlaying="y", side="right", autoshift=True, titlefont=dict(color="#1F2544"),tickfont=dict(color="#1F2544")),
#             yaxis7=dict(title="Sales", anchor="free", overlaying="y", autoshift=True, titlefont=dict(color="#0A2342"),tickfont=dict(color="#0A2342")),
#             legend=dict(bordercolor='rgba(255,255,255,0.5)', borderwidth=2, bgcolor='rgba(255,255,255,0.5)', orientation='h')  # Customize legend border
#         )
#     }
#     return figure