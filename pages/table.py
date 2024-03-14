import dash
from dash import dcc, html, dash_table, callback, Output, Input, State
import pandas as pd
import dash_bootstrap_components as dbc
from datetime import datetime
from dash.exceptions import PreventUpdate


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
                html.H3("Order History"),
            ], xs=6, sm=6, md=3, lg=6, xl=6, xxl=6, align="center"),

            dbc.Col([
                dbc.Button([
                    html.I(className="fa-solid fa-plus"),
                    " Add Order"
                ], id='open', n_clicks=0)
            ], xs=6, sm=6, md=3, lg=6, xl=6, xxl=6, className="d-flex justify-content-end"),
        ], style={'padding-bottom': '20px'}, align="start"),
        
        html.Div(id='status-div'),
        
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Add Order")),
                dbc.ModalBody([
                    html.P(children="", id="add-order-error"),       
                    dbc.Row([
                        dbc.Col([
                            dbc.Label('Order ID'),
                            dbc.Input(id='order-id', placeholder='Enter Order ID')
                        ], xs=12, sm=12, md=12, lg=12, xl=12, xxl=12, className="p-2"),
                        dbc.Col([
                            dbc.Label('Product ID'),
                            dbc.Input(id='product-id', placeholder='Enter Product ID')
                        ], xs=12, sm=12, md=12, lg=12, xl=12, xxl=12, className="p-2"),
                        dbc.Col([
                            dbc.Label('Customer ID'),
                            dbc.Input(id='customer-id', placeholder='Enter Customer ID')
                        ], xs=12, sm=12, md=12, lg=12, xl=12, xxl=12, className="p-2"),
                        dbc.Col([
                            dbc.Label('Quantity'),
                            dbc.Input(id='quantity-id', placeholder='Enter Quantity')
                        ], xs=12, sm=12, md=12, lg=12, xl=12, xxl=12, className="p-2"),
                        dbc.Col([
                            dbc.Label('Discount'),
                            dbc.Input(id='discount-id', placeholder='Enter Discount (0 - 1)')
                        ], xs=12, sm=12, md=12, lg=12, xl=12, xxl=12, className="p-2"),
                    ],  style={'padding': '5px 0px'}),
                ]),
                dbc.ModalFooter([
                    dbc.Button(
                        "Close", id="close", className="ms-auto", n_clicks=0
                    ),
                    dbc.Button(
                        "Add Order", id='button-add', n_clicks=0
                    )
                ]),
            ],
            id="modal",
            is_open=False,
        ),
        dbc.Row([
            dbc.Col([
                dcc.Dropdown(
                    id='country-dropdown',
                    options=country_options,
                    value=None,
                    placeholder="Select a country"
                )
            ], xs=12, sm=12, md=3, lg=2, xl=2, xxl=2, align="center"),
            dbc.Col([
                dcc.Dropdown(
                    id='state-dropdown',
                    options=[],
                    value=None,
                    placeholder="Select a state"
                )
            ], xs=12, sm=12, md=3, lg=2, xl=2, xxl=2, align="center"),
            dbc.Col([
                dcc.Dropdown(
                    id='city-dropdown',
                    options=[],
                    value=None,
                    placeholder="Select a city"
                )
            ], xs=12, sm=12, md=3, lg=2, xl=2, xxl=2, align="center"),

        ], className="filterDiv", justify="start"),

        dcc.Interval(
            id='alert-clear-interval',
            interval=3000,
            n_intervals=0,
            disabled=True
        ),

        dbc.Row([
            dash_table.DataTable(
                id='records-datatable',
                data=df.to_dict('records'),
                columns=[{"name": i, "id": i} for i in df.columns],
                page_size=10,
                style_as_list_view=True,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left'},
                markdown_options={"html": True}
            )
        ]),

    ], className="table-div"
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
    Output("modal", "is_open", allow_duplicate=True),
    [
        Input("open", "n_clicks"), 
        Input("close", "n_clicks"), 
    ],
    [State("modal", "is_open")],
    prevent_initial_call=True
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@callback(
    [Output('state-dropdown', 'options'),
     Output('state-dropdown', 'value')],
    [Input('country-dropdown', 'value')]
)
def set_states_options(selected_country):
    if selected_country is not None:
        states = df[df['Country'] == selected_country]['State'].unique()
        return [{'label': state, 'value': state} for state in states], None
    return [], None


@callback(
    [Output('city-dropdown', 'options'),
     Output('city-dropdown', 'value')],
    [Input('country-dropdown', 'value'),
     Input('state-dropdown', 'value')]
)
def set_cities_options(selected_country, selected_state):
    if selected_country and selected_state:
        filtered_df = df[(df['Country'] == selected_country) & (df['State'] == selected_state)]
        cities = filtered_df['City'].unique()
        return [{'label': city, 'value': city} for city in cities], None
    return [], None


@callback(
    Output('records-datatable', 'data', allow_duplicate=True),
    [Input('country-dropdown', 'value'),
     Input('state-dropdown', 'value'),
     Input('city-dropdown', 'value')],
    prevent_initial_call=True
)
def update_table(selected_country, selected_state, selected_city):

    
    filtered_df = df.copy()
    filtered = False

    if selected_country:
        filtered = True
        filtered_df = filtered_df[filtered_df['Country'] == selected_country]

    if selected_state:
        filtered = True
        filtered_df = filtered_df[filtered_df['State'] == selected_state]

    if selected_city:
        filtered = True
        filtered_df = filtered_df[filtered_df['City'] == selected_city]
    
    if not filtered:
        raise PreventUpdate

    return filtered_df.to_dict('records')


@callback(
    [
        Output('records-datatable', 'data'),
        Output('order-id', 'value'),
        Output('product-id', 'value'),
        Output('customer-id', 'value'),
        Output('quantity-id', 'value'),
        Output('discount-id', 'value'),
        Output('status-div', 'children'),
        Output('add-order-error', 'children'),
        Output('alert-clear-interval', 'disabled'),
        Output("modal", "is_open")
    ],
    [
        Input('button-add', 'n_clicks')
    ],
    [
        State('order-id', 'value'),
        State('product-id', 'value'),
        State('customer-id', 'value'),
        State('quantity-id', 'value'),
        State('discount-id', 'value'),
        State('records-datatable', 'data')
    ]
)
def add_entry_to_table(n_clicks, order_id, product_id, customer_id, quantity_id, discount_id, existing_data):
    if n_clicks > 0:
        if not order_id or not product_id:
            error = "Order ID and Product ID are required."
            return dash.no_update, order_id, product_id, customer_id, quantity_id, discount_id, dash.no_update, error, True, True
        
        for record in existing_data:
            if record['Order ID'] == order_id and record['Product ID'] == product_id:
                error = "This order and product combination already exists."
                return dash.no_update, order_id, product_id, customer_id, quantity_id, discount_id, dash.no_update, error, True, True

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
        return existing_data, None, None, None, None, None, success_alert, "", False, False

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, "", True, False
