import requests
import json
import numpy as np
import pandas as pd


class Data():
    def __init__(self, symbol):
        self.key = 'ADD TDA API KEY HERE'
        self.symbol = symbol.upper()
        #self.option_chain = self.get_option_chain()
        #self.ohlc = self.get_ohlc()

    def get_option_chain(self):
        url = 'https://api.tdameritrade.com/v1/marketdata/chains'
        option_req = requests.get(url=url, params={'apikey' : self.key, 'symbol' : self.symbol})
        option_json = json.loads(option_req.content)
        option_data = list(pd.json_normalize(option_json).iloc[:, 12:].iloc[0])
        option_df = pd.DataFrame([opt_dict for opt_list in option_data for opt_dict in opt_list])
        option_df.replace(-999, np.nan, inplace=True)
        option_df.replace('NaN', np.nan, inplace=True)
        option_df['quote'] = option_json['underlyingPrice']
        option_df['moneyness'] = np.log(option_df['strikePrice']/option_df['quote'])

        return option_df

    def get_ohlc(self):
        url = 'https://api.tdameritrade.com/v1/marketdata/{ticker}/pricehistory'.format(ticker=self.symbol)
        req = requests.get(url=url, params={'apikey' : self.key, 'period' : '2', 'periodType' : 'year', 'frequency' : '1', 'frequencyType' : 'daily'})
        req_json = json.loads(req.content)['candles']
        ohlc_df = pd.json_normalize(req_json)
        ohlc_df['date'] = pd.to_datetime(ohlc_df['datetime'],unit='ms').dt.date
        ohlc_df.drop(columns=['datetime'], inplace=True)
        ohlc_df.set_index(['date'], inplace=True)
        ohlc_df['returns'] = ohlc_df['close'].pct_change()
        ohlc_df['log_returns'] = np.log1p(ohlc_df['returns'])

        return ohlc_df

        