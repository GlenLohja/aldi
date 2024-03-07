import dash
from dash import dcc, html, dash_table, callback, Output, Input, State
import pandas as pd
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from datetime import datetime


dash.register_page(__name__, name='DataTable')

df = pd.read_excel('data/sample.xlsx', engine='openpyxl', sheet_name='Orders')

df['Order Date'] = df['Order Date'].dt.strftime('%Y-%m-%d')
df['Ship Date'] = df['Ship Date'].dt.strftime('%Y-%m-%d')
df = df.sort_values(by='Order Date', ascending=False)

unique_countries = df['Country'].unique()
country_options = [{'label': country, 'value': country} for country in unique_countries]

layout = html.Div(
    [   
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='country-dropdown',
                    options=country_options,
                    value=None,
                    placeholder="Select a country"
                )
            ], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2, align="center"),
            dbc.Col([
                dcc.Dropdown(
                    id='state-dropdown',
                    options=[],
                    value=None,
                    placeholder="Select a state"
                )
            ], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2, align="center"),
            dbc.Col([
                dcc.Dropdown(
                    id='city-dropdown',
                    options=[],
                    value=None,
                    placeholder="Select a city"
                )
            ], xs=4, sm=4, md=2, lg=2, xl=2, xxl=2, align="center")
        ], style={'padding': '10px 0px'}, justify="end"),

        dcc.Interval(
            id='alert-clear-interval',
            interval=3000,
            n_intervals = 0,
            disabled=True
        ),
        html.Div(id='status-div'),


        dbc.Row([
            dash_table.DataTable(
                id='records-datatable',
                data=df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in df.columns],
                page_size=10,
                fixed_rows={'headers': True},
                style_cell={'textAlign': 'left'},
            )
        ]),

        dbc.Row([
            dbc.Col(dbc.Input(id='order-id', placeholder='Enter Order ID')),
            dbc.Col(dbc.Input(id='product-id', placeholder='Enter Product ID')),
            dbc.Col(dbc.Input(id='customer-id', placeholder='Enter Customer ID')),
            dbc.Col(dbc.Input(id='quantity-id', placeholder='Enter Quantity')),
            dbc.Col(dbc.Input(id='discount-id', placeholder='Enter Discount (0 - 1)')),
            dbc.Col(dbc.Button('Add', id='button-add', n_clicks=0))
        ]),


    ]
)


@callback(
    [Output('status-div', 'children', allow_duplicate=True),
     Output('alert-clear-interval', 'disabled', allow_duplicate=True),
     Output('alert-clear-interval', 'n_intervals')],
    Input('alert-clear-interval', 'n_intervals'),
    prevent_initial_call=True
)
def clear_alert(n_intervals):
    if n_intervals > 0:
        return None, True, 0
    return dash.no_update, dash.no_update, dash.no_update    

@callback(
    Output('state-dropdown', 'options'),
    [Input('country-dropdown', 'value')]
)
def set_states_options(selected_country):
    if selected_country is not None:
        states = df[df['Country'] == selected_country]['State'].unique()
        return [{'label': state, 'value': state} for state in states]
    return []


@callback(
    Output('city-dropdown', 'options'),
    [Input('country-dropdown', 'value'),
     Input('state-dropdown', 'value')]
)
def set_cities_options(selected_country, selected_state):
    if selected_country and selected_state:
        filtered_df = df[(df['Country'] == selected_country) & (df['State'] == selected_state)]
        cities = filtered_df['City'].unique()
        return [{'label': city, 'value': city} for city in cities]
    return []


@callback(
    Output('records-datatable', 'data', allow_duplicate=True),
    [Input('country-dropdown', 'value'),
     Input('state-dropdown', 'value'),
     Input('city-dropdown', 'value'),],
    prevent_initial_call=True
)
def update_table(selected_country, selected_state, selected_city):
    filtered_df = df.copy()

    if selected_country:
        filtered_df = filtered_df[filtered_df['Country'] == selected_country]
    if selected_state:
        filtered_df = filtered_df[filtered_df['State'] == selected_state]
    if selected_city:
        filtered_df = filtered_df[filtered_df['City'] == selected_city]

    if filtered_df.empty:
        return df.to_dict('records')

    return filtered_df.to_dict('records')


@callback(
    [Output('records-datatable', 'data'),
    Output('order-id', 'value'),
    Output('product-id', 'value'),
    Output('customer-id', 'value'),
    Output('quantity-id', 'value'),
    Output('discount-id', 'value'),
    Output('status-div', 'children'),
    Output('alert-clear-interval', 'disabled')],
    [Input('button-add', 'n_clicks')],
    [State('order-id', 'value'),
    State('product-id', 'value'),
    State('customer-id', 'value'),
    State('quantity-id', 'value'),
    State('discount-id', 'value'),
    State('records-datatable', 'data')]
)
def add_entry_to_table(n_clicks, order_id, product_id, customer_id, quantity_id, discount_id, existing_data):
    if n_clicks > 0:
        if not order_id or not product_id:
            error_alert = dbc.Alert("Order ID and Product ID are required.", color="danger")
            return dash.no_update, None, None, None, None, None, error_alert, False
        
        for record in existing_data:
            if record['Order ID'] == order_id and record['Product ID'] == product_id:
                error_alert = dbc.Alert("This order and product combination already exists.", color="danger")
                return dash.no_update, None, None, None, None, None, error_alert, False

        new_entry = {
            'Order ID': order_id,
            'Product ID': product_id,
            'Customer ID': customer_id,
            'Quantity': quantity_id,
            'Discount': discount_id,
            'Order Date': datetime.today().strftime('%Y-%m-%d')
        }
        existing_data.insert(0, new_entry)
        success_alert = dbc.Alert("Entry added successfully!", color="success")
        return existing_data, None, None, None, None, None, success_alert, False

    return existing_data, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, True
