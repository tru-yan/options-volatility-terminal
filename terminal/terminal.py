import dash
from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
from dash.dependencies import Input, Output, State
import data
import ivol
import rvol
import oi_volume
import greeks


class Terminal():
    def __init__(self):
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

        vol_menu = dbc.DropdownMenu(
            label="Volatility Analysis",
            children=[
                dbc.DropdownMenuItem("Implied Volatility", href="/ivol"),
                dbc.DropdownMenuItem("Realized Volatility", href="/rvol"),
            ],
            color='dark',
            style={},
            caret=False
        )

        option_menu = dbc.DropdownMenu(
            label="Option Analysis",
            children=[
                dbc.DropdownMenuItem("Open Interest and Volume", href="/oi_volume"),
                dbc.DropdownMenuItem("Greeks", href="/greeks"),
            ],
            color='dark',
            style={},
            caret=False
        )

        navbar = dbc.Navbar([
            dbc.Row([
                dbc.Col(
                    dbc.Input(type="search", value="AMD", id='ticker-symbol', style={'margin-left': 10})
                    ),
                dbc.Col(
                    dbc.Button(dbc.Spinner("Run!", id='spinner'), color="primary", style={'margin-left': 12}, id='run'), 
                    width="auto"
                    ),
                ],
                className="g-0",
                align="center",
            ),
            vol_menu,
            option_menu],
            color="dark",
            dark=True,
            sticky="top"
        )

        content = html.Div(id="page-content")

        self.app.layout = html.Div(children=[dcc.Location(id="url"), navbar, content])

        #initialize app callbacks
        self.callbacks()
        self.ivol = ivol.ivol(self.app)
        self.rvol = rvol.rvol(self.app)
        self.oi_volume = oi_volume.oi_volume(self.app)
        self.greeks = greeks.greeks(self.app)

    def callbacks(self):
        @self.app.callback(Output("page-content", "children"), Output("spinner", "children"), [Input("url", "pathname"), Input("run", "n_clicks"), State("ticker-symbol", "value")])
        def render_page_content(pathname, n, symbol):
            ticker = data.Data(symbol)

            run = "Run!"

            if pathname == "/rvol":
                stock_data = ticker.get_ohlc()
                rvol_page = self.rvol.load_page(stock_data, ticker.symbol)
                return [rvol_page, run]
            elif pathname == "/oi_volume":
                option_data = ticker.get_option_chain()
                oi_volume_page = self.oi_volume.load_page(option_data, ticker.symbol)
                return [oi_volume_page, run]
            elif pathname == "/greeks":
                option_data = ticker.get_option_chain()
                greeks_page = self.greeks.load_page(option_data, ticker.symbol)
                return [greeks_page, run]
            else:
                option_data = ticker.get_option_chain()
                ivol_page = self.ivol.load_page(option_data, ticker.symbol)
                return [ivol_page, run]

            # If the user tries to reach a different page, return a 404 message

if __name__ == '__main__':
    terminal = Terminal()
    terminal.app.run_server(debug=True, port=2)