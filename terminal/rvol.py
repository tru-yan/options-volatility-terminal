import dash_bootstrap_components as dbc
from dash import dcc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output


class rvol():
    def __init__(self, app):
        self.app = app
        self.callbacks(self.app)

    def load_page(self, data, symbol):
        self.data = data
        self.symbol = symbol

        vol_cone_menu = dbc.Col([
            dcc.Dropdown(
                    id='vol_cone_dropdown',
                    options=[
                        {'label': 'Quantiles', 'value': 'quantiles'},
                        {'label': 'Distribution', 'value': 'distribution'}
                    ],
                    value='quantiles',
                    searchable=False,
                    clearable=False
            )],
            style={'color': 'black', 'margin-left': 'auto', 'margin-right': 0},
            width=6, xs=6)

        vol_est_menu = dbc.Col([
            dcc.Dropdown(
                    id='vol_est_dropdown',
                    options=[
                        {'label': '2 Weeks', 'value': '2wk'},
                        {'label': '1 Month', 'value': '1mo'},
                        {'label': '3 Months', 'value': '3mo'},
                        {'label': '6 Months', 'value': '6mo'},
                        {'label': '1 Year', 'value': '1yr'}
                    ],
                    value='1mo',
                    searchable=False,
                    clearable=False
            )],
            style={'color': 'black', 'margin-left': 'auto', 'margin-right': 0},
            width=6, xs=6)

        ts_time_menu = dbc.Col([
            dcc.Dropdown(
                    id='ts_time_dropdown',
                    options=[
                        {'label': 'Close-To-Close', 'value': 'close_to_close'},
                        {'label': 'Parkinson', 'value': 'parkinson'},
                        {'label': 'Garman-Klass', 'value': 'garman_klass'},
                        {'label': 'Rogers-Satchell', 'value': 'rogers_satchell'},
                        {'label': 'Yang-Zhang', 'value': 'yang_zhang'},
                        {'label': 'Avergae', 'value': 'average'}
                    ],
                    value='close_to_close',
                    searchable=False,
                    clearable=False
            )],
            style={'color': 'black', 'margin-left': 'auto', 'margin-right': 0},
            width=6, xs=6)

        self.page = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.Navbar(children=["Realized Volatility Term Structure", ts_time_menu], color='dark', style={'border-radius': '0.5em', 'height': '3em'}),
                    dbc.CardBody(
                        dcc.Graph(id='ts_time_fig', style={"height": "25em"})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True,
                    inverse=True),
                dbc.Card([
                    dbc.Navbar(children=["Realized Volatility Estimation", vol_est_menu], color='dark', style={'border-radius': '0.5em', 'height': '3em'}),
                    dbc.CardBody(
                        dcc.Graph(id='vol_est_fig', style={"height": "25em"})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True,
                    inverse=True)
            ], width=6, xs=6),
            dbc.Col([
                dbc.Card([
                    dbc.Navbar(children=["Realized Volatility Cone", vol_cone_menu], color='dark', style={'border-radius': '0.5em', 'height': '3em'}),
                    dbc.CardBody(
                        dcc.Graph(id='vol_cone_fig', style={"height": "25em"})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True,
                    inverse=True),
                dbc.Card([
                    dbc.Navbar("Realized Volatility Forecast", color='dark', style={'border-radius': '0.5em', 'height': '3em'}),
                    dbc.CardBody(
                        dcc.Graph(id='vol_forecast', style={"height": "25em"})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True,
                    inverse=True)
            ], width=6, xs=6)],
            className="g-0")

        return [self.page]

    def get_yang_zhang(self, window):
        log_ho = (self.data['high'] / self.data['open']).apply(np.log)
        log_lo = (self.data['low'] / self.data['open']).apply(np.log)
        log_co = (self.data['close'] / self.data['open']).apply(np.log)
        
        log_oc = (self.data['open'] / self.data['close'].shift(1)).apply(np.log)
        log_oc_sq = log_oc**2
        
        log_cc = (self.data['close'] / self.data['close'].shift(1)).apply(np.log)
        log_cc_sq = log_cc**2
        
        rs = log_ho * (log_ho - log_co) + log_lo * (log_lo - log_co)
        
        close_vol = log_cc_sq.rolling(
            window=window,
            center=False
        ).sum() * (1.0 / (window - 1.0))
        open_vol = log_oc_sq.rolling(
            window=window,
            center=False
        ).sum() * (1.0 / (window - 1.0))
        window_rs = rs.rolling(
            window=window,
            center=False
        ).sum() * (1.0 / (window - 1.0))

        k = 0.34 / (1.34 + (window + 1) / (window - 1))
        result = (open_vol + k * close_vol + (1 - k) * window_rs).apply(np.sqrt) * np.sqrt(252)
        
        return result

    def get_close_to_close(self, window):
        return self.data['log_returns'].rolling(window).std()*np.sqrt(252)
    
    def get_parkinson(self, window):
        return np.sqrt(np.square(np.log(self.data['high']/self.data['low'])).rolling(window).sum()*(1/(4*window*np.log(2))))*np.sqrt(252)

    def get_garman_klass(self, window):
        return np.sqrt(0.5*np.square(np.log(self.data['high']/self.data['low'])).rolling(window).sum()*(1/window)-(2*np.log(2)-1)*np.square(np.log(self.data['close']/self.data['open'])).rolling(window).sum()*(1/window))*np.sqrt(252)

    def get_rogers_satchell(self, window):
        return np.sqrt((np.log(self.data['high']/self.data['close'])*np.log(self.data['high']/self.data['open'])+np.log(self.data['low']/self.data['close'])*np.log(self.data['low']/self.data['open'])).rolling(window).sum()*(1/window))*np.sqrt(252)

    def get_average_est(self, window):
        self.data['close_to_close'] = self.get_close_to_close(window)
        self.data['parkinson'] = self.get_parkinson(window)
        self.data['garman_klass'] = self.get_garman_klass(window)
        self.data['rogers_satchell'] = self.get_rogers_satchell(window)
        self.data['yang_zhang'] = self.get_yang_zhang(window)
        return self.data[['close_to_close', 'parkinson', 'garman_klass', 'rogers_satchell', 'yang_zhang']].mean(axis=1)

    def get_time_ts(self, est):
        ts_time_df = pd.DataFrame()

        if est == 'close_to_close':
            ts_time_df['2wk_rvol'] = self.get_close_to_close(10)
            ts_time_df['1mo_rvol'] = self.get_close_to_close(21)
            ts_time_df['3mo_rvol'] = self.get_close_to_close(63)
            ts_time_df['6mo_rvol'] = self.get_close_to_close(126)
            ts_time_df['1yr_rvol'] = self.get_close_to_close(252)
        elif est == 'parkinson':
            ts_time_df['2wk_rvol'] = self.get_parkinson(10)
            ts_time_df['1mo_rvol'] = self.get_parkinson(21)
            ts_time_df['3mo_rvol'] = self.get_parkinson(63)
            ts_time_df['6mo_rvol'] = self.get_parkinson(126)
            ts_time_df['1yr_rvol'] = self.get_parkinson(252)
        elif est == 'garman_klass':
            ts_time_df['2wk_rvol'] = self.get_garman_klass(10)
            ts_time_df['1mo_rvol'] = self.get_garman_klass(21)
            ts_time_df['3mo_rvol'] = self.get_garman_klass(63)
            ts_time_df['6mo_rvol'] = self.get_garman_klass(126)
            ts_time_df['1yr_rvol'] = self.get_garman_klass(252)
        elif est == 'rogers_satchell':
            ts_time_df['2wk_rvol'] = self.get_rogers_satchell(10)
            ts_time_df['1mo_rvol'] = self.get_rogers_satchell(21)
            ts_time_df['3mo_rvol'] = self.get_rogers_satchell(63)
            ts_time_df['6mo_rvol'] = self.get_rogers_satchell(126)
            ts_time_df['1yr_rvol'] = self.get_rogers_satchell(252)
        elif est == 'yang_zhang':
            ts_time_df['2wk_rvol'] = self.get_yang_zhang(10)
            ts_time_df['1mo_rvol'] = self.get_yang_zhang(21)
            ts_time_df['3mo_rvol'] = self.get_yang_zhang(63)
            ts_time_df['6mo_rvol'] = self.get_yang_zhang(126)
            ts_time_df['1yr_rvol'] = self.get_yang_zhang(252)
        elif est == 'average':
            ts_time_df['2wk_rvol'] = self.get_average_est(10)
            ts_time_df['1mo_rvol'] = self.get_average_est(21)
            ts_time_df['3mo_rvol'] = self.get_average_est(63)
            ts_time_df['6mo_rvol'] = self.get_average_est(126)
            ts_time_df['1yr_rvol'] = self.get_average_est(252)

        return ts_time_df

    def get_quantile_vol_cone(self):
        rvol = self.get_time_ts('close_to_close')
        ts_df = pd.DataFrame(rvol.iloc[-1, -5:].values, columns=['rvol'])
        ts_df['days'] = [10, 21, 63, 126, 252]
        ts_df['max_rvol'] = [rvol['2wk_rvol'].max(), rvol['1mo_rvol'].max(), rvol['3mo_rvol'].max(), rvol['6mo_rvol'].max(), rvol['1yr_rvol'].max()]
        ts_df['min_rvol'] = [rvol['2wk_rvol'].min(), rvol['1mo_rvol'].min(), rvol['3mo_rvol'].min(), rvol['6mo_rvol'].min(), rvol['1yr_rvol'].min()]
        ts_df['mean_rvol'] = [rvol['2wk_rvol'].mean(), rvol['1mo_rvol'].mean(), rvol['3mo_rvol'].mean(), rvol['6mo_rvol'].mean(), rvol['1yr_rvol'].mean()]
        ts_df['median_rvol'] = [rvol['2wk_rvol'].median(), rvol['1mo_rvol'].median(), rvol['3mo_rvol'].median(), rvol['6mo_rvol'].median(), rvol['1yr_rvol'].median()]
        ts_df['25pct_rvol'] = [rvol['2wk_rvol'].quantile(0.25), rvol['1mo_rvol'].quantile(0.25), rvol['3mo_rvol'].quantile(0.25), rvol['6mo_rvol'].quantile(0.25), rvol['1yr_rvol'].quantile(0.25)]
        ts_df['75pct_rvol'] = [rvol['2wk_rvol'].quantile(0.75), rvol['1mo_rvol'].quantile(0.75), rvol['3mo_rvol'].quantile(0.75), rvol['6mo_rvol'].quantile(0.75), rvol['1yr_rvol'].quantile(0.75)]

        return ts_df

    def get_distribution_vol_cone(self):
        rvol = self.get_time_ts('close_to_close')
        ts_df = pd.DataFrame(rvol.iloc[-1, -5:].values, columns=['rvol'])
        ts_df['days'] = [10, 21, 63, 126, 252]
        ts_df['mean_rvol'] = [rvol['2wk_rvol'].mean(), rvol['1mo_rvol'].mean(), rvol['3mo_rvol'].mean(), rvol['6mo_rvol'].mean(), rvol['1yr_rvol'].mean()]
        ts_df['down1std_rvol'] = [rvol['2wk_rvol'].mean()-rvol['2wk_rvol'].std(), rvol['1mo_rvol'].mean()-rvol['1mo_rvol'].std(), rvol['3mo_rvol'].mean()-rvol['3mo_rvol'].std(), rvol['6mo_rvol'].mean()-rvol['6mo_rvol'].std(), rvol['1yr_rvol'].mean()-rvol['1yr_rvol'].std()]
        ts_df['up1std_rvol'] = [rvol['2wk_rvol'].mean()+rvol['2wk_rvol'].std(), rvol['1mo_rvol'].mean()+rvol['1mo_rvol'].std(), rvol['3mo_rvol'].mean()+rvol['3mo_rvol'].std(), rvol['6mo_rvol'].mean()+rvol['6mo_rvol'].std(), rvol['1yr_rvol'].mean()+rvol['1yr_rvol'].std()]
        ts_df['down2std_rvol'] = [rvol['2wk_rvol'].mean()-2*rvol['2wk_rvol'].std(), rvol['1mo_rvol'].mean()-2*rvol['1mo_rvol'].std(), rvol['3mo_rvol'].mean()-2*rvol['3mo_rvol'].std(), rvol['6mo_rvol'].mean()-2*rvol['6mo_rvol'].std(), rvol['1yr_rvol'].mean()-2*rvol['1yr_rvol'].std()]
        ts_df['up2std_rvol'] = [rvol['2wk_rvol'].mean()+2*rvol['2wk_rvol'].std(), rvol['1mo_rvol'].mean()+2*rvol['1mo_rvol'].std(), rvol['3mo_rvol'].mean()+2*rvol['3mo_rvol'].std(), rvol['6mo_rvol'].mean()+2*rvol['6mo_rvol'].std(), rvol['1yr_rvol'].mean()+2*rvol['1yr_rvol'].std()]
        ts_df['down3std_rvol'] = [rvol['2wk_rvol'].mean()-3*rvol['2wk_rvol'].std(), rvol['1mo_rvol'].mean()-3*rvol['1mo_rvol'].std(), rvol['3mo_rvol'].mean()-3*rvol['3mo_rvol'].std(), rvol['6mo_rvol'].mean()-3*rvol['6mo_rvol'].std(), rvol['1yr_rvol'].mean()-3*rvol['1yr_rvol'].std()]
        ts_df['up3std_rvol'] = [rvol['2wk_rvol'].mean()+3*rvol['2wk_rvol'].std(), rvol['1mo_rvol'].mean()+3*rvol['1mo_rvol'].std(), rvol['3mo_rvol'].mean()+3*rvol['3mo_rvol'].std(), rvol['6mo_rvol'].mean()+3*rvol['6mo_rvol'].std(), rvol['1yr_rvol'].mean()+3*rvol['1yr_rvol'].std()]

        return ts_df

    def get_vol_est(self, window):
        vol_est_df = pd.DataFrame()
        vol_est_df['close_to_close'] = self.get_close_to_close(window)
        vol_est_df['parkinson'] = self.get_parkinson(window)
        vol_est_df['garman_klass'] = self.get_garman_klass(window)
        vol_est_df['rogers_satchell'] = self.get_rogers_satchell(window)
        vol_est_df['yang_zhang'] = self.get_yang_zhang(window)
        vol_est_df['average'] = self.get_average_est(window)

        return vol_est_df

    def get_rvol_forecast(self):
        ...

    def callbacks(self, app):
        
        @app.callback(Output('vol_cone_fig', 'figure'), [Input('vol_cone_dropdown', 'value')])
        def update_vol_cone(value):
            vol_cone = go.Figure()

            if value == 'quantiles':
                ts_df = self.get_quantile_vol_cone()

                vol_cone.add_trace(go.Scatter(x=ts_df['days'], y=ts_df['rvol'], name='Current'))
                vol_cone.add_trace(go.Scatter(x=ts_df['days'], y=ts_df['mean_rvol'], name='Mean'))
                vol_cone.add_trace(go.Scatter(x=ts_df['days'], y=ts_df['max_rvol'], name='Max'))
                vol_cone.add_trace(go.Scatter(x=ts_df['days'], y=ts_df['75pct_rvol'], name='75%'))
                vol_cone.add_trace(go.Scatter(x=ts_df['days'], y=ts_df['median_rvol'], name='Median'))
                vol_cone.add_trace(go.Scatter(x=ts_df['days'], y=ts_df['25pct_rvol'], name='25%'))
                vol_cone.add_trace(go.Scatter(x=ts_df['days'], y=ts_df['min_rvol'], name='Min'))
            elif value == 'distribution':
                ts_df = self.get_distribution_vol_cone()

                vol_cone.add_trace(go.Scatter(x=ts_df['days'], y=ts_df['rvol'], name='Current'))
                vol_cone.add_trace(go.Scatter(x=ts_df['days'], y=ts_df['mean_rvol'], name='Mean'))
                vol_cone.add_trace(go.Scatter(x=ts_df['days'], y=ts_df['down1std_rvol'], name='1std_down'))
                vol_cone.add_trace(go.Scatter(x=ts_df['days'], y=ts_df['up1std_rvol'], name='1std_up'))
                vol_cone.add_trace(go.Scatter(x=ts_df['days'], y=ts_df['down2std_rvol'], name='2std_down'))
                vol_cone.add_trace(go.Scatter(x=ts_df['days'], y=ts_df['up2std_rvol'], name='2std_up'))
                vol_cone.add_trace(go.Scatter(x=ts_df['days'], y=ts_df['down3std_rvol'], name='3std_down'))
                vol_cone.add_trace(go.Scatter(x=ts_df['days'], y=ts_df['up3std_rvol'], name='3std_up'))

            vol_cone.update_xaxes(title_text='Days')
            vol_cone.update_yaxes(title_text='Realized Volatility')
            vol_cone.update_layout(margin=dict(l=0, r=0, t=0, b=0))
            
            return vol_cone

        @app.callback(Output('vol_est_fig', 'figure'), [Input('vol_est_dropdown', 'value')])
        def update_vol_est(value):
            window = 21

            if value == '2wk':
                window = 10
            elif value == '1mo':
                window = 21
            elif value == '3mo':
                window = 63
            elif value == '6mo':
                window = 126
            elif value == '1yr':
                window = 252

            vol_est_df = self.get_vol_est(window)

            vol_est = go.Figure()
            vol_est.add_trace(go.Scatter(x=vol_est_df.index[window:], y=vol_est_df['close_to_close'][window:], name='Close-to-Close'))
            vol_est.add_trace(go.Scatter(x=vol_est_df.index[window:], y=vol_est_df['parkinson'][window:], name='Parkinson'))
            vol_est.add_trace(go.Scatter(x=vol_est_df.index[window:], y=vol_est_df['garman_klass'][window:], name='Garman-Klass'))
            vol_est.add_trace(go.Scatter(x=vol_est_df.index[window:], y=vol_est_df['rogers_satchell'][window:], name='Rogers-Satchell'))
            vol_est.add_trace(go.Scatter(x=vol_est_df.index[window:], y=vol_est_df['yang_zhang'][window:], name='Yang-Zhang'))
            vol_est.add_trace(go.Scatter(x=vol_est_df.index[window:], y=vol_est_df['average'][window:], name='Average'))
            vol_est.update_xaxes(title_text='Date')
            vol_est.update_yaxes(title_text='Realized Volatility')
            vol_est.update_layout(legend_title_text='Estimation', margin=dict(l=0, r=0, t=0, b=0))

            return vol_est

        @app.callback(Output('ts_time_fig', 'figure'), [Input('ts_time_dropdown', 'value')])
        def update_ts_time(value):
            ts_df = self.get_time_ts(value)

            ts = go.Figure()
            ts.add_trace(go.Scatter(x=ts_df.index, y=ts_df['2wk_rvol'], name='2 Weeks'))
            ts.add_trace(go.Scatter(x=ts_df.index, y=ts_df['1mo_rvol'], name='1 Month'))
            ts.add_trace(go.Scatter(x=ts_df.index, y=ts_df['3mo_rvol'], name='3 Months'))
            ts.add_trace(go.Scatter(x=ts_df.index, y=ts_df['6mo_rvol'], name='6 Months'))
            ts.add_trace(go.Scatter(x=ts_df.index, y=ts_df['1yr_rvol'], name='1 Year'))
            ts.update_xaxes(title_text='Date')
            ts.update_yaxes(title_text='Realized Volatility')
            ts.update_layout(legend_title_text='Period', margin=dict(l=0, r=0, t=0, b=0))

            return ts