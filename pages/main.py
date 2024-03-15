import dash
from dash import dcc, html, callback, Output, Input
import pandas as pd
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import calendar
from components.card import create_card

dash.register_page(__name__, path='/', name='Home')

df = pd.read_excel('data/sample.xlsx', engine='openpyxl', sheet_name='Orders')


def summarize_sales_data(df, year):
    # Summarizes sales data for a given year.
    df_year = df[df['Order Date'].dt.year == year].copy()
    df_year['Month'] = df_year['Order Date'].dt.month

    # Group by Month for Sales and Profit Summary
    grouped_sales = df_year.groupby('Month')[['Sales', 'Profit']].sum().reset_index()
    grouped_sales['Month Name'] = grouped_sales['Month'].apply(lambda x: calendar.month_name[x])
    grouped_sales['Profit Ratio'] = grouped_sales['Profit'] / grouped_sales['Sales']

    # Group by Product for Quantity Summary
    grouped_products = df_year.groupby(['Product ID', 'Product Name'])['Quantity'].sum().reset_index()
    top_10_products = grouped_products.sort_values(by='Quantity', ascending=False).head(10)
    
    return grouped_sales, top_10_products


grouped_sales_df, top_10_products = summarize_sales_data(df, 2017)


def aggregate_sales_data(df, year, month):
    # Aggregate sales data for a given year and month.

    df_filtered = df[(df['Order Date'].dt.year == year) & (df['Order Date'].dt.month == month)]
    grouped_df = df_filtered.groupby('Order Date').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order Date': 'count'
    }).rename(columns={'Order Date': 'Count'}).reset_index()

    grouped_df['Profit Ratio'] = grouped_df['Profit'] / grouped_df['Sales']
    grouped_df['Day'] = grouped_df['Order Date'].dt.day

    return grouped_df

# current_year = datetime.now().year
# current_month = datetime.now().month


grouped_current_month_df = aggregate_sales_data(df, 2017, 12)
grouped_prev_month_df = aggregate_sales_data(df, 2017, 11)

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
    f"{profit_ratio}%"
)


layout = html.Div([
    dbc.Row([
        dbc.Col([
            sales_card
        ], xs=12, sm=12, md=4, lg=4, xl=4, xxl=4, align="center"),
        dbc.Col([
            profit_card
        ], xs=12, sm=12, md=4, lg=4, xl=4, xxl=4, align="center"),
        dbc.Col([
            profit_ratio_card
        ], xs=12, sm=12, md=4, lg=4, xl=4, xxl=4, align="center"),
    ], style={'padding': '10px 0px'}),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='combo-chart',
                figure={
                    'data': [
                        go.Bar(
                            x=grouped_sales_df['Month Name'],
                            y=grouped_sales_df['Sales'],
                            name='Sales',
                            marker=dict(color='#427D9D') 
                        ),
                        go.Bar(
                            x=grouped_sales_df['Month Name'],
                            y=grouped_sales_df['Profit'],
                            name='Profit',
                            marker=dict(color='#9BBEC8') 
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
                        title='Sales, Profit, and Profit Ratio Over Time',
                        xaxis=dict(title='Date'),
                        yaxis=dict(title='Amount', side='left', rangemode='tozero'),
                        yaxis2=dict(title='Ratio %', side='right', overlaying='y', rangemode='tozero', tickformat='.0%'),
                        barmode='group',
                        legend=dict(bordercolor='rgba(255,255,255,0.5)', borderwidth=2, bgcolor='rgba(255,255,255,0.5)',
                                    orientation='h')
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
                            x=top_10_products['Quantity'],
                            y=top_10_products['Product ID'],
                            orientation='h',
                            marker=dict(color='#427D9D')
                        )
                    ],
                    'layout': go.Layout(
                        title='Product Value',
                        xaxis=dict(title='Quantity'),
                        yaxis=dict(title='Product', autorange='reversed'),
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
                            x=grouped_prev_month_df['Order Date'],
                            y=grouped_prev_month_df['Profit Ratio'],
                            mode='lines+markers',
                            marker=dict(color='#B5C0D0'),
                            name='Previous Month'
                        ),
                        go.Scatter(
                            x=grouped_current_month_df['Order Date'],
                            y=grouped_current_month_df['Profit Ratio'],
                            mode='lines+markers',
                            marker=dict(color='#40679E'),
                            name='Current Month'
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
                            x=grouped_current_month_df['Order Date'],
                            y=grouped_current_month_df['Count'],
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
