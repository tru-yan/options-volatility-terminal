import dash_bootstrap_components as dbc
from dash import dcc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output
from dash import dash_table


class ivol():
    def __init__(self, app):
        self.app = app
        self.callbacks(self.app)

    def load_page(self, data, symbol):
        self.data = data
        self.symbol = symbol

        iv_surface_menu = dbc.Col([
        dcc.Dropdown(
                id='iv_surface_dropdown',
                options=[
                    {'label': 'Strike Price', 'value': 'strike'},
                    {'label': 'Moneyness', 'value': 'moneyness'}
                ],
                value='strike',
                searchable=False,
                clearable=False
        )],
        style={'color': 'black', 'margin-left': 'auto', 'margin-right': 0},
        width=6, xs=6)

        ts_menu = dbc.Col([
            dcc.Dropdown(
                id='ts_dropdown',
                options=[
                    {'label': 'ATM', 'value': 'atm'},
                    {'label': 'Delta', 'value': 'delta'}
                ],
                value='atm',
                searchable=False,
                clearable=False
        )],
        style={'color': 'black', 'margin-left': 'auto', 'margin-right': 0},
        width=6, xs=6)

        iv_smile_menu = dbc.Col([
            dcc.Dropdown(
                id='iv_smile_dropdown',
                options=[
                    {'label': 'Strike Price', 'value': 'strike'},
                    {'label': 'Moneyness', 'value': 'moneyness'}
                ],
                value='strike',
                searchable=False,
                clearable=False
        )],
        style={'color': 'black', 'margin-left': 'auto', 'margin-right': 0},
        width=3, xs=3)

        skew_menu = dbc.Col([
            dcc.Dropdown(
                id='skew_dropdown',
                options=[
                    {'label': 'Strike Skew', 'value': 'strike_skew'},
                    {'label': 'Delta Skew', 'value': 'delta_skew'}
                ],
                value='strike_skew',
                searchable=False,
                clearable=False
        )],
        style={'color': 'black', 'margin-left': 'auto', 'margin-right': 0},
        width=6, xs=6)

        row1 = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.Navbar(children=['IV Surface', iv_surface_menu], color='dark', style={'height': '3em', 'border-radius': '0.5em'}),
                    dbc.CardBody(
                        dcc.Graph(id='iv_surface_fig', style={"height": "25em"})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True,
                    inverse=True),
            ], width=6, xs=6),
            dbc.Col([
                dbc.Card([
                    dbc.Navbar(children=['  Term Structure', ts_menu], color='dark', style={'height': '3em', 'border-radius': '0.5em'}),
                    dbc.CardBody(
                        dcc.Graph(id='ts_fig', style={"height": "25em"})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True,
                    inverse=True),
            ], width=6, xs=6)],
            className="g-0")

        row2 = dbc.Card([
                    dbc.Navbar(children=["  IV Curves", iv_smile_menu], color='dark', style={'height': '3em', 'border-radius': '0.5em'}),
                    dbc.CardBody(
                        dcc.Graph(id='iv_smile_fig', style={"height": "25em"})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True,
                    inverse=True)

        row3 = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.Navbar(children=["  Skew Term Structure", skew_menu], color='dark', style={'height': '3em', 'border-radius': '0.5em'}),
                dbc.CardBody(
                    dcc.Graph(id='skew_fig', style={"height": "25em"})
                )], 
                style={"padding": "1em"}, 
                color="white",
                outline=True,
                inverse=True),
        ], width=6, xs=6)],
        className="g-0")

        return [row1, row2, row3]

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

    def get_delta_ts(self):
        option_df = self.data
        option_df['50_call_delta_diff'] = abs(option_df['delta'] - 0.5)
        option_df['50_put_delta_diff'] = abs(option_df['delta'] - -0.5)
        option_df['25_call_delta_diff'] = abs(option_df['delta'] - 0.25)
        option_df['25_put_delta_diff'] = abs(option_df['delta'] - -0.25)
        call_50_ts_df = pd.DataFrame()
        put_50_ts_df = pd.DataFrame()
        call_25_ts_df = pd.DataFrame()
        put_25_ts_df = pd.DataFrame()

        for exp in option_df['daysToExpiration'].unique():
            exp_df = option_df[option_df['daysToExpiration'] == exp]
            min_50_call_diff = exp_df[exp_df['50_call_delta_diff'] == exp_df['50_call_delta_diff'].min()]
            min_50__put_diff = exp_df[exp_df['50_put_delta_diff'] == exp_df['50_put_delta_diff'].min()]
            min_25_call_diff = exp_df[exp_df['25_call_delta_diff'] == exp_df['25_call_delta_diff'].min()]
            min_25_put_diff = exp_df[exp_df['25_put_delta_diff'] == exp_df['25_put_delta_diff'].min()]
            call_50_ts_df = pd.concat([call_50_ts_df, min_50_call_diff], ignore_index=True)
            put_50_ts_df = pd.concat([put_50_ts_df, min_50__put_diff], ignore_index=True)
            call_25_ts_df = pd.concat([call_25_ts_df, min_25_call_diff], ignore_index=True)
            put_25_ts_df = pd.concat([put_25_ts_df, min_25_put_diff], ignore_index=True)

        return [call_50_ts_df, put_50_ts_df, call_25_ts_df, put_25_ts_df]

    def get_strike_skew(self):
        option_df = self.data
        option_df['110_moneyness_diff'] = abs(option_df['moneyness'] - 0.1)
        option_df['90_moneyness_diff'] = abs(option_df['moneyness'] - (-0.1))
        ts_df = pd.DataFrame()

        for exp in option_df['daysToExpiration'].unique():
            exp_df = option_df[option_df['daysToExpiration'] == exp]
            min_110 = exp_df[exp_df['110_moneyness_diff'] == exp_df['110_moneyness_diff'].min()].iloc[0]
            min_90 = exp_df[exp_df['90_moneyness_diff'] == exp_df['90_moneyness_diff'].min()].iloc[0]
            test = pd.DataFrame(data={'volatility': [(min_90['volatility'] - min_110['volatility'])], 'daysToExpiration': [min_110['daysToExpiration']]})
            ts_df = pd.concat([ts_df, test], ignore_index=True)

        return ts_df

    def get_delta_skew(self):
        option_df = self.data
        option_df['25_call_delta_diff'] = abs(option_df['delta'] - 0.25)
        option_df['25_put_delta_diff'] = abs(option_df['delta'] - (-0.25))
        option_df['50_delta_diff'] = abs(option_df['delta'] - 0.5)
        ts_df = pd.DataFrame()

        for exp in option_df['daysToExpiration'].unique():
            exp_df = option_df[option_df['daysToExpiration'] == exp]
            min_25_call = exp_df[exp_df['25_call_delta_diff'] == exp_df['25_call_delta_diff'].min()].iloc[0]
            min_25_put = exp_df[exp_df['25_put_delta_diff'] == exp_df['25_put_delta_diff'].min()].iloc[0]
            min_50_delta = exp_df[exp_df['50_delta_diff'] == exp_df['50_delta_diff'].min()].iloc[0]
            delta_skew_df = pd.DataFrame(data={'volatility': [(min_25_put['volatility'] - min_25_call['volatility'])/min_50_delta['volatility']], 'daysToExpiration': [min_50_delta['daysToExpiration']]})
            ts_df = pd.concat([ts_df, delta_skew_df], ignore_index=True)

        return ts_df

    def callbacks(self, app):

        @app.callback(Output('ts_fig', 'figure'), [Input('ts_dropdown', 'value')])
        def update_ts(value):
            ts = go.Figure()

            if value == 'atm':
                ts_df = self.get_ts()
                ts.add_trace(go.Scatter(x=ts_df[1]['daysToExpiration'], y=ts_df[1]['volatility'], name='Call'))
                ts.add_trace(go.Scatter(x=ts_df[0]['daysToExpiration'], y=ts_df[0]['volatility'], name='Put'))
            elif value == 'delta':
                ts_df = self.get_delta_ts()
                ts.add_trace(go.Scatter(x=ts_df[0]['daysToExpiration'], y=ts_df[0]['volatility'], name='50 delta call'))
                ts.add_trace(go.Scatter(x=ts_df[1]['daysToExpiration'], y=ts_df[1]['volatility'], name='50 delta put'))
                ts.add_trace(go.Scatter(x=ts_df[2]['daysToExpiration'], y=ts_df[2]['volatility'], name='25 delta call'))
                ts.add_trace(go.Scatter(x=ts_df[3]['daysToExpiration'], y=ts_df[3]['volatility'], name='25 delta put'))

            ts.update_layout(margin=dict(l=0, r=0, t=0, b=0), legend_title_text='Option Type')
            ts.update_xaxes(title_text='DTE')
            ts.update_yaxes(title_text='IV')
            ts.update_traces(connectgaps=True)

            return ts

        @app.callback(Output('iv_surface_fig', 'figure'), [Input('iv_surface_dropdown', 'value')])
        def update_iv_surface(value):
            option_data = self.data
            iv_surface = go.Figure()

            if value == 'strike':
                iv_surface = go.Figure(data=[go.Mesh3d(x=option_data['strikePrice'], y=option_data['daysToExpiration'], z=option_data['volatility'], opacity=1, intensity=option_data['volatility'], colorbar_title='IV')])
                iv_surface.update_layout(scene=dict(xaxis_title='Strike Price', yaxis_title='DTE', zaxis_title='IV'), margin=dict(l=0, r=0, t=0, b=0))

            elif value == 'moneyness':
                iv_surface = go.Figure(data=[go.Mesh3d(x=option_data['moneyness'], y=option_data['daysToExpiration'], z=option_data['volatility'], opacity=1, intensity=option_data['volatility'], colorbar_title='IV')])
                iv_surface.update_layout(scene=dict(xaxis_title='Moneyness', yaxis_title='DTE', zaxis_title='IV'), margin=dict(l=0, r=0, t=0, b=0))

            return iv_surface

        @app.callback(Output('iv_smile_fig', 'figure'), [Input('iv_smile_dropdown', 'value')])
        def update_iv_curves(value):
            option_data = self.data
            iv_smile = go.Figure()

            if value == 'strike':
                iv_smile = px.line(option_data, x='strikePrice', y='volatility', color='daysToExpiration', facet_col='putCall', facet_col_spacing=0.1)
                iv_smile.update_xaxes(title='Strike Price')
                iv_smile.add_vline(x=option_data['quote'].mean(), line_dash='dash', annotation_text=self.symbol + ': ' + str(round(option_data['quote'].mean(), 2)))

            elif value == 'moneyness':
                iv_smile = px.line(option_data, x='moneyness', y='volatility', color='daysToExpiration', facet_col='putCall', facet_col_spacing=0.1)
                iv_smile.update_xaxes(title='Moneyness')
                iv_smile.add_vline(x=0, line_dash='dash', annotation_text=self.symbol + ': ' + str(round(option_data['quote'].mean(), 2)))

            iv_smile.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
            iv_smile.update_yaxes(title='IV')
            iv_smile.update_layout(legend_title_text='DTE', margin=dict(l=0, r=0, t=15, b=0))
            iv_smile.update_traces(connectgaps=True)

            return iv_smile

        @app.callback(Output('skew_fig', 'figure'), [Input('skew_dropdown', 'value')])
        def update_skew(value):
            skew = go.Figure()

            if value == 'strike_skew':
                skew_df = self.get_strike_skew()
                skew.add_trace(go.Scatter(x=skew_df['daysToExpiration'], y=skew_df['volatility']))
            elif value == 'delta_skew':
                skew_df = self.get_delta_skew()
                skew.add_trace(go.Scatter(x=skew_df['daysToExpiration'], y=skew_df['volatility']))

            skew.update_xaxes(title_text='DTE')
            skew.update_yaxes(title_text='Skew')
            skew.update_traces(connectgaps=True)
            skew.update_layout(margin=dict(l=0, r=0, t=0, b=0))

            return skew

