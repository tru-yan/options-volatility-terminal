import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from dash import dash_table

class oi_volume():
    def __init__(self, app):
        self.app = app
        self.callbacks(self.app)
    
    def load_page(self, data, symbol):
        self.data = data
        self.symbol = symbol

        opt_type_menu1 = dbc.Col([
            dcc.Dropdown(
                    id='opt_type_menu1',
                    options=[
                        {'label': 'Total', 'value': 'total'},
                        {'label': 'Option Type', 'value': 'option_type'},
                    ],
                    value='total',
                    searchable=False,
                    clearable=False
            )],
            style={'color': 'black', 'margin-left': 'auto', 'margin-right': 0},
            width=6, xs=6)

        opt_type_menu2 = dbc.Col([
            dcc.Dropdown(
                    id='opt_type_menu2',
                    options=[
                        {'label': 'Total', 'value': 'total'},
                        {'label': 'Option Type', 'value': 'option_type'},
                    ],
                    value='total',
                    searchable=False,
                    clearable=False
            )],
            style={'color': 'black', 'margin-left': 'auto', 'margin-right': 0},
            width=6, xs=6)
        
        opt_type_menu3 = dbc.Col([
            dcc.Dropdown(
                    id='opt_type_menu3',
                    options=[
                        {'label': 'Total', 'value': 'total'},
                        {'label': 'Option Type', 'value': 'option_type'},
                    ],
                    value='total',
                    searchable=False,
                    clearable=False
            )],
            style={'color': 'black', 'margin-left': 'auto', 'margin-right': 0},
            width=6, xs=6)
        
        opt_type_menu4 = dbc.Col([
            dcc.Dropdown(
                    id='opt_type_menu4',
                    options=[
                        {'label': 'Total', 'value': 'total'},
                        {'label': 'Option Type', 'value': 'option_type'},
                    ],
                    value='total',
                    searchable=False,
                    clearable=False
            )],
            style={'color': 'black', 'margin-left': 'auto', 'margin-right': 0},
            width=6, xs=6)

        row1 = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.Navbar(children=["Open Interest By Strike", opt_type_menu1], color='dark', style={'border-radius': '0.5em', 'height': '3em'}),
                    dbc.CardBody(
                        dcc.Graph(id='oi_strike_fig', style={"height": "25em"})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True,
                    inverse=True),
                dbc.Card([
                    dbc.Navbar(children=["Volume By Strike", opt_type_menu2], color='dark', style={'border-radius': '0.5em', 'height': '3em'}),
                    dbc.CardBody(
                        dcc.Graph(id='vol_strike_fig', style={"height": "25em"})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True,
                    inverse=True),
            ], width=6, xs=6),
            dbc.Col([
                dbc.Card([
                    dbc.Navbar(children=["Open Interest By Expiration", opt_type_menu3], color='dark', style={'border-radius': '0.5em', 'height': '3em'}),
                    dbc.CardBody(
                        dcc.Graph(id='oi_exp_fig', style={"height": "25em"})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True,
                    inverse=True),
                dbc.Card([
                    dbc.Navbar(children=["Volume By Expiration", opt_type_menu4], color='dark', style={'border-radius': '0.5em', 'height': '3em'}),
                    dbc.CardBody(
                        dcc.Graph(id='vol_exp_fig', style={"height": "25em"})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True,
                    inverse=True),
            ], width=6, xs=6)],
            className="g-0")

        oi_strike_df = self.data.groupby('strikePrice')['openInterest'].sum()
        oi_strike_df = round((oi_strike_df/oi_strike_df.sum()), 4).nlargest(10).to_frame()
        oi_strike_df.reset_index(inplace=True)

        oi_exp_df = self.data.groupby('daysToExpiration')['openInterest'].sum()
        oi_exp_df = round((oi_exp_df/oi_exp_df.sum()), 4).nlargest(10).to_frame()
        oi_exp_df.reset_index(inplace=True)

        vol_strike_df = self.data.groupby('strikePrice')['totalVolume'].sum()
        vol_strike_df = round((vol_strike_df/vol_strike_df.sum()), 4).nlargest(10).to_frame()
        vol_strike_df.reset_index(inplace=True)

        vol_exp_df = self.data.groupby('daysToExpiration')['totalVolume'].sum()
        vol_exp_df = round((vol_exp_df/vol_exp_df.sum()), 4).nlargest(10).to_frame()
        vol_exp_df.reset_index(inplace=True)

        self.call_df = self.split_data()[0]
        self.put_df = self.split_data()[1]

        row2 = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.Navbar(children=["Top 10 Percentile OI (STRIKE)"], color='dark', style={'color':'white', 'border-radius': '0.5em', 'height': '3em'}),
                    dbc.CardBody(
                        dash_table.DataTable(columns=[{"name": i, "id": i} for i in oi_strike_df.columns], data=oi_strike_df.to_dict('records'), style_cell={'textAlign': 'left'})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True)
            ], width=3, xs=3),
            dbc.Col([
                dbc.Card([
                    dbc.Navbar(children=["Top 10 Percentile OI (EXP)"], color='dark', style={'color':'white', 'border-radius': '0.5em', 'height': '3em'}),
                    dbc.CardBody(
                        dash_table.DataTable(columns=[{"name": i, "id": i} for i in oi_exp_df.columns], data=oi_exp_df.to_dict('records'), style_cell={'textAlign': 'left'})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True)
            ], width=3, xs=3),
            dbc.Col([
                dbc.Card([
                    dbc.Navbar(children=["Top 10 Percentile Volume (STRIKE)"], color='dark', style={'color':'white', 'border-radius': '0.5em', 'height': '3em'}),
                    dbc.CardBody(
                        dash_table.DataTable(columns=[{"name": i, "id": i} for i in vol_strike_df.columns], data=vol_strike_df.to_dict('records'), style_cell={'textAlign': 'left'})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True)
            ], width=3, xs=3),
            dbc.Col([
                dbc.Card([
                    dbc.Navbar(children=["Top 10 Percentile Volume (EXP)"], color='dark', style={'color':'white', 'border-radius': '0.5em', 'height': '3em'}),
                    dbc.CardBody(
                        dash_table.DataTable(columns=[{"name": i, "id": i} for i in vol_exp_df.columns], data=vol_exp_df.to_dict('records'), style_cell={'textAlign': 'left'})
                    )], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True)
            ], width=3, xs=3)
            ],
            className="g-0")

        row3 = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.Navbar(children=["Open Interest Stats"], color='dark', style={'color':'white', 'border-radius': '0.5em', 'height': '3em'}),
                    dbc.CardBody(children=[
                        html.P("Total Open Interest: " + str(self.data['openInterest'].sum())),
                        html.P("Total Call Open Interest: " + str(self.call_df['openInterest'].sum())),
                        html.P("Call Open Interest Percentage: " + str(round(self.call_df['openInterest'].sum()/self.data['openInterest'].sum(), 4))),
                        html.P("Total Put Open Interest: " + str(self.put_df['openInterest'].sum())),
                        html.P("Put Open Interest Percentage: " + str(round(self.put_df['openInterest'].sum()/self.data['openInterest'].sum(), 4))),
                        html.P("Put-Call Ratio: " + str(round(self.put_df['openInterest'].sum()/self.call_df['openInterest'].sum(), 4)))
                    ])], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True)
            ], width=6, xs=6),
            dbc.Col([
                dbc.Card([
                    dbc.Navbar(children=["Volume Stats"], color='dark', style={'color':'white', 'border-radius': '0.5em', 'height': '3em'}),
                    dbc.CardBody(children=[
                        html.P("Total Volume: " + str(self.data['totalVolume'].sum())),
                        html.P("Total Call Volume: " + str(self.call_df['totalVolume'].sum())),
                        html.P("Call Volume Percentage: " + str(round(self.call_df['totalVolume'].sum()/self.data['totalVolume'].sum(), 4))),
                        html.P("Total Put Volume: " + str(self.put_df['totalVolume'].sum())),
                        html.P("Put Volume Percentage: " + str(round(self.put_df['totalVolume'].sum()/self.data['totalVolume'].sum(), 4))),
                        html.P("Put-Call Ratio: " + str(round(self.put_df['totalVolume'].sum()/self.call_df['totalVolume'].sum(), 4)))
                    ])], 
                    style={"padding": "1em"}, 
                    color="white",
                    outline=True)
            ], width=6, xs=6)],
            className="g-0")

        return [row1, row2, row3]

    def split_data(self):
        call_df = self.data[self.data['putCall'] == 'CALL'].sort_values(['daysToExpiration', 'strikePrice'], ignore_index=True)
        put_df = self.data[self.data['putCall'] == 'PUT'].sort_values(['daysToExpiration', 'strikePrice'], ignore_index=True)
    
        return [call_df, put_df]

    def callbacks(self, app):
        
        @app.callback(Output('oi_strike_fig', 'figure'), [Input('opt_type_menu1', 'value')])
        def update_oi_strike(value):
            fig = go.Figure()

            if value == 'total':
                oi_strike_df = self.data.groupby('strikePrice')['openInterest'].sum()
                fig.add_trace(go.Bar(x=oi_strike_df.index, y=oi_strike_df))
            elif value == 'option_type':
                data = self.split_data()
                puts = data[1].groupby('strikePrice')['openInterest'].sum()
                calls = data[0].groupby('strikePrice')['openInterest'].sum()

                fig.add_trace(go.Bar(x=calls.index, y=calls, name='calls'))
                fig.add_trace(go.Bar(x=puts.index, y=puts, name='puts'))
                

            fig.update_xaxes(type='category')
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))

            return fig

        @app.callback(Output('oi_exp_fig', 'figure'), [Input('opt_type_menu3', 'value')])
        def update_oi_exp(value):
            fig = go.Figure()

            if value == 'total':
                oi_exp_df = self.data.groupby('daysToExpiration')['openInterest'].sum()
                fig.add_trace(go.Bar(x=oi_exp_df.index, y=oi_exp_df))
            elif value == 'option_type':
                data = self.split_data()
                puts = data[1].groupby('daysToExpiration')['openInterest'].sum()
                calls = data[0].groupby('daysToExpiration')['openInterest'].sum()

                fig.add_trace(go.Bar(x=calls.index, y=calls, name='calls'))
                fig.add_trace(go.Bar(x=puts.index, y=puts, name='puts'))
                

            fig.update_xaxes(type='category')
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))

            return fig

        @app.callback(Output('vol_strike_fig', 'figure'), [Input('opt_type_menu2', 'value')])
        def update_vol_strike(value):
            fig = go.Figure()

            if value == 'total':
                vol_strike_df = self.data.groupby('strikePrice')['totalVolume'].sum()
                fig.add_trace(go.Bar(x=vol_strike_df.index, y=vol_strike_df))
            elif value == 'option_type':
                data = self.split_data()
                puts = data[1].groupby('strikePrice')['totalVolume'].sum()
                calls = data[0].groupby('strikePrice')['totalVolume'].sum()
                
                fig.add_trace(go.Bar(x=calls.index, y=calls, name='calls'))
                fig.add_trace(go.Bar(x=puts.index, y=puts, name='puts'))
                

            fig.update_xaxes(type='category')
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))

            return fig

        @app.callback(Output('vol_exp_fig', 'figure'), [Input('opt_type_menu4', 'value')])
        def update_vol_exp(value):
            fig = go.Figure()

            if value == 'total':
                vol_exp_df = self.data.groupby('daysToExpiration')['totalVolume'].sum()
                fig.add_trace(go.Bar(x=vol_exp_df.index, y=vol_exp_df))
            elif value == 'option_type':
                data = self.split_data()
                puts = data[1].groupby('daysToExpiration')['totalVolume'].sum()
                calls = data[0].groupby('daysToExpiration')['totalVolume'].sum()

                fig.add_trace(go.Bar(x=calls.index, y=calls, name='calls'))
                fig.add_trace(go.Bar(x=puts.index, y=puts, name='puts'))
                

            fig.update_xaxes(type='category')
            fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))

            return fig