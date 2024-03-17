import dash
from dash import dcc, html, callback, Output, Input
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import calendar
from components.card import create_card

dash.register_page(__name__, path='/', name='Home')

df = pd.read_excel('data/sample.xlsx', engine='openpyxl', sheet_name='Orders')
unique_years = sorted(df['Order Date'].dt.year.unique(), reverse=True)
latest_year = unique_years[0]
latest_year_df = df[df['Order Date'].dt.year == latest_year]
latest_month = latest_year_df['Order Date'].dt.month.max()


def summarize_sales_data(dataframe, year):
    # Summarizes sales data for a given year.
    df_year = dataframe[dataframe['Order Date'].dt.year == year].copy()
    df_year['Month'] = df_year['Order Date'].dt.month

    # Group by Month for Sales and Profit Summary
    grouped_sales = df_year.groupby('Month')[['Sales', 'Profit']].sum().reset_index()
    grouped_sales['Month Name'] = grouped_sales['Month'].apply(lambda x: calendar.month_name[x])
    grouped_sales['Profit Ratio'] = grouped_sales['Profit'] / grouped_sales['Sales']

    # Group by Product for Quantity Summary
    grouped_products = df_year.groupby(['Product ID', 'Product Name'])['Quantity'].sum().reset_index()
    top_10_products = grouped_products.sort_values(by='Quantity', ascending=False).head(10)
    
    return grouped_sales, top_10_products


def aggregate_sales_data(dataframe, year, month):
    # Aggregate sales data for a given year and month.

    df_filtered = dataframe[(dataframe['Order Date'].dt.year == year) & (dataframe['Order Date'].dt.month == month)]
    grouped_df = df_filtered.groupby('Order Date').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order Date': 'count'
    }).rename(columns={'Order Date': 'Count'}).reset_index()

    grouped_df['Profit Ratio'] = grouped_df['Profit'] / grouped_df['Sales']
    grouped_df['Day'] = grouped_df['Order Date'].dt.day

    return grouped_df


# Generate options for a month and year component
year_options = [{'label': year, 'value': year} for year in unique_years]
month_options = [{'label': month, 'value': str(index)} for index, month in enumerate(calendar.month_name) if month]

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Select(
                    id='year-selector',
                    options=year_options,
                    value=2017
                ),
        ], xs=12, sm=12, md=12, lg=6, xl=2, xxl=2, className="p-2"),
        dbc.Col([
            dbc.Select(
                    id='month-selector',
                    options=month_options,
                    value=12
                ),
        ], xs=12, sm=12, md=12, lg=6, xl=2, xxl=2, className="p-2")
    ], className="justify-content-end pb-2"),

    dbc.Row([
        dbc.Col([], xs=12, sm=12, md=4, lg=4, xl=4, xxl=4, id="sales-col"),
        dbc.Col([], xs=12, sm=12, md=4, lg=4, xl=4, xxl=4, id="profit-col"),
        dbc.Col([], xs=12, sm=12, md=4, lg=4, xl=4, xxl=4, id="profit-ratio-col"),
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='monthly-chart'
            )
        ], xs=12, sm=12, md=12, lg=6, xl=8, xxl=8, className="p-2"),
        dbc.Col([
            dcc.Graph(
                id='sold-products-chart'
            )
        ], xs=12, sm=12, md=12, lg=6, xl=4, xxl=4, className="p-2")
    ], className='py-2'),

    dbc.Row([
        dbc.Col([
            dbc.Select(
                id='property-selector',
                options=[
                    {'label': 'Profit', 'value': 'Profit'},
                    {'label': 'Sales', 'value': 'Sales'},
                    {'label': 'Profit Ratio', 'value': 'Profit Ratio'}
                ],
                value='Profit Ratio'
            )
        ], className="property-dropdown")
    ], className="compare-months"),

    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='timeline-chart'
            )
        ], xs=12, sm=12, md=12, lg=6, xl=8, xxl=8, className="p-2"),
        dbc.Col([
            dcc.Graph(
                id='orders-chart'
            )
        ], xs=12, sm=12, md=12, lg=6, xl=4, xxl=4, className="p-2")
    ], className='py-2'),
], className="px-3")


@callback(
    [
        Output('sales-col', 'children'),
        Output('profit-col', 'children'),
        Output('profit-ratio-col', 'children')
    ],
    Input('year-selector', 'value')

)
def update_cards(year_selected):
    grouped_sales_df, top_10_products = summarize_sales_data(df, int(year_selected))
    sales_card = create_card(
        "fa-solid fa-sack-dollar",
        "Total Sales",
        f"{round(grouped_sales_df['Sales'].sum(), 2):,.0f}$"
    )

    profit_card = create_card(
        "fa-solid fa-hand-holding-dollar",
        "Total Profit",
        f"{round(grouped_sales_df['Profit'].sum(), 2):,.0f}$"
    )

    profit_ratio = round(grouped_sales_df['Profit'].sum() / grouped_sales_df['Sales'].sum(), 3) * 100
    profit_ratio_card = create_card(
        "fa-solid fa-piggy-bank",
        "Profit Ratio",
        f"{profit_ratio:.1f}%"
    )

    return sales_card, profit_card, profit_ratio_card


@callback(
    [
        Output('monthly-chart', 'figure'),
        Output('sold-products-chart', 'figure'),
    ],
    [
        Input('year-selector', 'value'),
    ]
)
def update_monthly_charts(year_selected):
    # most recent year is selected initially
    grouped_sales_df, top_10_products = summarize_sales_data(df, int(year_selected))

    monthly_figure = {
        'data': [
            go.Bar(
                x=grouped_sales_df['Month Name'],
                y=grouped_sales_df['Sales'],
                name='Sales',
                marker=dict(color='#427D9D'),
                hovertemplate="<b>%{x}</b><br>$%{y:,.0f} Sales</br>"
            ),
            go.Bar(
                x=grouped_sales_df['Month Name'],
                y=grouped_sales_df['Profit'],
                name='Profit',
                marker=dict(color='#9BBEC8'),
                hovertemplate="<b>%{x}</b><br>$%{y:,.0f} Profit</br>"
            ),
            go.Scatter(
                x=grouped_sales_df['Month Name'],
                y=grouped_sales_df['Profit Ratio'],
                yaxis='y2',
                mode='lines+markers',
                name='Profit Ratio',
                line=dict(color='#164863')
            )
        ],
        'layout': go.Layout(
            title=f'Monthly Sales, Profit & Profit Ratio - {year_selected}',
            # xaxis=dict(title='Date'),
            yaxis=dict(title='Profit & Sales', side='left', rangemode='tozero'),
            yaxis2=dict(title='Ratio %', side='right', overlaying='y', rangemode='tozero', tickformat='.0%'),
            barmode='group',
            legend=dict(bordercolor='rgba(255,255,255,0.5)', borderwidth=2, bgcolor='rgba(255,255,255,0.5)',
                        orientation='h')
        )
    }

    products_figure = {
        'data': [
            go.Bar(
                x=top_10_products['Quantity'],
                y=top_10_products['Product ID'],
                orientation='h',
                marker=dict(color='#427D9D'),
                customdata=top_10_products['Product Name'],
                hovertemplate="<b>Quantity: %{x}</b><br>%{customdata}</br>"
            )
        ],
        'layout': go.Layout(
            title=f'Top 10 Products - {year_selected}',
            xaxis=dict(title='Quantity'),
            yaxis=dict(title='Product', autorange='reversed'),
            margin=dict(l=170),
            height=450
        )
    }
    return monthly_figure, products_figure


@callback(
    [
        Output('timeline-chart', 'figure'),
        Output('orders-chart', 'figure')
    ],
    [
        Input('property-selector', 'value'),
        Input('year-selector', 'value'),
        Input('month-selector', 'value')
    ]
)
def update_timeline_chart(property_selected, year_selected, month_selected):
    
    grouped_current_month_df = aggregate_sales_data(df, int(year_selected), int(month_selected))

    prev_month = int(month_selected) - 1
    prev_month_year = int(year_selected)
    if prev_month == 0:
        prev_month = 12
        prev_month_year -= 1

    grouped_prev_month_df = aggregate_sales_data(df, prev_month_year, prev_month)

    yaxis = {
        "title": property_selected
    }
    if property_selected == 'Profit Ratio':
        yaxis['tickformat'] = '.0%'

    revenue_fig = {
        'data': [
            go.Scatter(
                x=grouped_prev_month_df['Order Date'],
                y=grouped_prev_month_df[property_selected],
                mode='lines+markers',
                marker=dict(color='#B5C0D0'),
                hovertemplate=f"<br>%{{x}}<br>{property_selected} : %{{y}}",
                name=f'{calendar.month_name[prev_month]}, {prev_month_year}'
            ),
            go.Scatter(
                x=grouped_current_month_df['Order Date'],
                y=grouped_current_month_df[property_selected],
                mode='lines+markers',
                marker=dict(color='#40679E'),
                hovertemplate=f"<br>%{{x}}<br>{property_selected} : %{{y}}",
                name=f'{calendar.month_name[int(month_selected)]}, {year_selected}'
            )
        ],
        'layout': go.Layout(
            title='Daily Trend',
            yaxis=yaxis,
            hovermode='x',
            legend=dict(bgcolor='rgba(255,255,255,0.5)', orientation='h')
        )
    }

    orders_fig = {
        'data': [
            go.Scatter(
                x=grouped_current_month_df['Order Date'],
                y=grouped_current_month_df['Count'],
                mode='lines',
                marker=dict(color='#40679E'),
                name='Past 30 Days'
            )
        ],
        'layout': go.Layout(
            title='Number Of Orders Timeline',
            xaxis=dict(title='Date'),
            yaxis=dict(title='Orders'),
            hovermode='x'
        )
    }

    return revenue_fig, orders_fig
