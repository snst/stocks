import yfinance as yf
import requests_cache
from sklearn.preprocessing import MinMaxScaler
from investor_constants import *


class Stock():
    def __init__(self, names, session, period, start, end):
        self.period = period
        self.start = start
        self.end = end
        tickers = yf.Ticker(names, session=session)
        self.hist = tickers.history(period=period, start=start, end=end)

    def is_same(self, period, start, end):
        return self.period == period and self.start == start and self.end == end


class StockLoader():
    def __init__(self):
        self.session = requests_cache.CachedSession('yfinance.cache')
        self.session.headers['User-agent'] = 'my-program/1.0'
        self.cache = {}

    def load(self, names, period=None, start=None, end=None):
        if names in self.cache:
            stock = self.cache[names]
            if stock.is_same(period, start, end):
                return stock.hist

        stock = Stock(names, self.session, period, start, end)
        self.cache[names] = stock
        return stock.hist

    def preprocess(self, name, settings):
        hist = self.cache.get(name, None)
        if hist:
            self.preprocess_hist(hist, settings)

    def preprocess_hist(self, hist, settings):
        last_close = None
        data = hist[D_CLOSE]
        data2 = []
        for d in data:
            data2.append([d])
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(data2)
        for i, (index, row) in enumerate(hist.iterrows()):
            hist.at[index, D_CLOSE_SCALED] = scaled[i]
            close = row[D_CLOSE]
            high = row[D_HIGH]
            low = row[D_LOW]
            spread = high - low
            hist.at[index, D_SPREAD] = spread
            if None == last_close:
                last_close = close
            delta = (100.0 * (close - last_close) / last_close)
            last_close = close
            hist.at[index, D_CLOSE_DELTA_PERCENT] = delta

            low3 = low + (1.0 - settings.minimum_reach) * (spread / 2.0)
            high3 = high - (1.0 - settings.maximum_reach) * (spread / 2.0)
            hist.at[index, D_LOW_3] = low3
            hist.at[index, D_HIGH_3] = high3
