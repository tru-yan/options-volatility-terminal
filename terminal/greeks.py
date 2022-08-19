import dash_bootstrap_components as dbc
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go


class greeks():
    def __init__(self, app):
        self.app = app
        self.callbacks(self.app)

    def load_page(self, data, symbol):
        self.data = data

        greeks_surface_menu = dbc.Col([
        dcc.Dropdown(
                id='greeks_surface_dropdown',
                options=[
                    {'label': 'Delta', 'value': 'delta'},
                    {'label': 'Gamma', 'value': 'gamma'},
                    {'label': 'Theta', 'value': 'theta'},
                    {'label': 'Rho', 'value': 'rho'},
                    {'label': 'Vega', 'value': 'vega'}
                ],
                value='delta',
                searchable=False,
                clearable=False
        )],
        style={'color': 'black', 'margin-left': 'auto', 'margin-right': 0},
        width=6, xs=6)

        greeks_ts_menu = dbc.Col([
        dcc.Dropdown(
                id='greeks_ts_dropdown',
                options=[
                    {'label': 'Delta', 'value': 'delta'},
                    {'label': 'Gamma', 'value': 'gamma'},
                    {'label': 'Theta', 'value': 'theta'},
                    {'label': 'Rho', 'value': 'rho'},
                    {'label': 'Vega', 'value': 'vega'}
                ],
                value='delta',
                searchable=False,
                clearable=False
        )],
        style={'color': 'black', 'margin-left': 'auto', 'margin-right': 0},
        width=6, xs=6)

        greeks_menu = dbc.Col([
        dcc.Dropdown(
                id='greeks_dropdown',
                options=[
                    {'label': 'Delta', 'value': 'delta'},
                    {'label': 'Gamma', 'value': 'gamma'},
                    {'label': 'Theta', 'value': 'theta'},
                    {'label': 'Rho', 'value': 'rho'},
                    {'label': 'Vega', 'value': 'vega'},
                    {'label': 'Time Value', 'value': 'timeValue'},
                    {'label': 'Bid Size', 'value': 'bidSize'},
                    {'label': 'Ask Size', 'value': 'askSize'},
                    {'label': 'Last Size', 'value': 'lastSize'},
                    {'label': 'Mark', 'value': 'mark'},
                    {'label': 'Bid', 'value': 'bid'},
                    {'label': 'Ask', 'value': 'ask'},
                    {'label': 'Last', 'value': 'last'},
                    {'label': 'High Price', 'value': 'highPrice'},
                    {'label': 'Low Price', 'value': 'lowPrice'},
                    {'label': 'Open Price', 'value': 'openPrice'},
                    {'label': 'Close Price', 'value': 'closePrice'},
                    {'label': 'Total Volume', 'value': 'totalVolume'},
                    {'label': 'Open Interest', 'value': 'openInterest'},
                    {'label': 'Percent Change', 'value': 'percentChange'},
                    {'label': 'Net Change', 'value': 'netChange'}
                ],
                value='delta',
                searchable=False,
                clearable=False
        )],
        style={'color': 'black', 'margin-left': 'auto', 'margin-right': 0},
        width=3, xs=3)

        row1 = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.Navbar(children=['Greek Surface', greeks_surface_menu], color='dark', style={'height': '3em', 'border-radius': '0.5em'}),
                    dbc.CardBody(
                        dcc.Graph(id='greek_surface_fig', style={"height": "25em"})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True,
                    inverse=True),
            ], width=6, xs=6),
            dbc.Col([
                dbc.Card([
                    dbc.Navbar(children=['Term Structure', greeks_ts_menu], color='dark', style={'height': '3em', 'border-radius': '0.5em'}),
                    dbc.CardBody(
                        dcc.Graph(id='greek_ts_fig', style={"height": "25em"})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True,
                    inverse=True),
            ], width=6, xs=6)])

        row2 = dbc.Card([
            dbc.Navbar(children=["Greeks", greeks_menu], color='dark', style={'height': '3em', 'border-radius': '0.5em'}),
            dbc.CardBody(
                dcc.Graph(id='greeks_fig', style={"height": "25em"})
            )], 
            style={"padding": "1em"}, 
            color="white",
            outline=True,
            inverse=True)

        return [row1, row2]

    def get_ts(self):
        option_df = self.data
        option_df['price_diff'] = abs(option_df['strikePrice'] - option_df['quote'])
        atm_ts_df = pd.DataFrame()

        for exp in option_df['daysToExpiration'].unique():
            exp_df = option_df[option_df['daysToExpiration'] == exp]
            min_price_diff = exp_df[exp_df['price_diff'] == exp_df['price_diff'].min()]
            atm_ts_df = pd.concat([atm_ts_df, min_price_diff], ignore_index=True)

        put_atm_ts_df = atm_ts_df[atm_ts_df['putCall'] == 'PUT'].sort_values(by='daysToExpiration').reset_index()
        call_atm_ts_df = atm_ts_df[atm_ts_df['putCall'] == 'CALL'].sort_values(by='daysToExpiration').reset_index()
        return [put_atm_ts_df, call_atm_ts_df]

    def callbacks(self, app):
        @app.callback(Output('greek_surface_fig', 'figure'), [Input('greeks_surface_dropdown', 'value')])
        def update_greek_surface(value):
            option_data = self.data
            greek_surface = go.Figure(data=[go.Mesh3d(x=option_data['strikePrice'], y=option_data['daysToExpiration'], z=option_data[value], opacity=1, intensity=option_data[value], colorbar_title=value)])
            greek_surface.update_layout(scene=dict(xaxis_title='Strike Price', yaxis_title='DTE', zaxis_title=value), margin=dict(l=0, r=0, t=0, b=0))

            return greek_surface

        @app.callback(Output('greek_ts_fig', 'figure'), [Input('greeks_ts_dropdown', 'value')])
        def update_greek_ts(value):
            ts = go.Figure()
            ts_df = self.get_ts()
            ts.add_trace(go.Scatter(x=ts_df[1]['daysToExpiration'], y=ts_df[1][value], name='Call'))
            ts.add_trace(go.Scatter(x=ts_df[0]['daysToExpiration'], y=ts_df[0][value], name='Put'))
            ts.update_layout(margin=dict(l=0, r=0, t=0, b=0), legend_title_text='Option Type')
            ts.update_xaxes(title_text='DTE')
            ts.update_yaxes(title_text=value)
            ts.update_traces(connectgaps=True)

            return ts

        @app.callback(Output('greeks_fig', 'figure'), [Input('greeks_dropdown', 'value')])
        def update_greeks(value):
            option_data = self.data
            fig = px.line(option_data, x='strikePrice', y=value, color='daysToExpiration', facet_col='putCall', facet_col_spacing=0.1)
            fig.update_yaxes(title=value)
            fig.update_xaxes(title='Strike Price')
            fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            fig.update_layout(legend_title_text='DTE', margin=dict(l=0, r=0, t=15, b=0))
            fig.update_traces(connectgaps=True)

            return fig
            