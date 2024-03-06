import dash
from dash import dcc, html, dash_table
import pandas as pd
import dash_bootstrap_components as dbc

dash.register_page(__name__, name='DataTable')

df = pd.read_excel('data/sample.xlsx', engine='openpyxl', sheet_name='Orders')

df['Order Date'] = df['Order Date'].dt.strftime('%Y-%m-%d')
df['Ship Date'] = df['Ship Date'].dt.strftime('%Y-%m-%d')


layout = html.Div(
    [
        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{"name": i, "id": i} for i in df.columns],
            page_size=10,
            fixed_rows={'headers': True},
            style_cell={'textAlign': 'left'},
        )
    ]
)