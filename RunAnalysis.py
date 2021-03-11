import yfinance as yf
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplfinance as mpf
import os
from DataScrape import GetData
from datetime import datetime


class Analysis:

    def __init__(self, symbol, days=25, period="1mo", interval="15m", symbol2=None, save=None):
        self.p1 = symbol
        self.p2 = symbol2
        self.days = days
        self.period = period
        self.interval = interval
        self.save = save
        self.path = "/PycharmProjects/Options/output/"
        self.stocklist = []
        # define series for Ichimoku
        self.tenkan = {}
        self.kijun = {}
        self.chikou = {}
        self.senkou_a = {}
        self.senkou_b = {}

    def find_50200ma_cross(self):
        """
        Sends a ticker to get the data from the list of Nasdaq tickers, grabs the actions (dividends, stock splits),
        calculates the 200ma, adjusts if any dividends or stock splits occured in that time.
        """
        # ToDo: need to do a lag and look at the previous 7 days to compare the 200ma/50ma cross to see the direction
        for i in GetData.get_stock_list():
            cross = False
            try:
                data = GetData(i)
                tikr_data = data.get_stock_data()
                tikr_actions = tikr_data.actions
                # tikrYrDy = tikr_data.history(period="1y", interval="1d")
                tikr_close = tikr_data.history()
                tikr_9ma = tikr_close["Close"].tail(9).mean()
                tikr_50ma = tikr_data.info["fiftyDayAverage"]
                tikr_200ma = tikr_close["Close"].tail(200).mean()
                last_close = tikr_close["Close"].tail(1)[0]
            except ValueError as e:
                # print(f"Not enough data, Exception: {e}")
                continue
            if 1 > tikr_50ma / tikr_200ma > 0.99 and \
                    last_close > tikr_9ma and \
                    tikr_50ma < last_close < tikr_200ma:
                cross = True
                print(f"{i}\n50ma: {tikr_50ma}\n200ma: {tikr_200ma}\nLast Close: {last_close}\n9ma: {tikr_9ma}\n")
            else:
                cross = False
            if cross:
                self.stocklist.append(i)

    def ichimoku(self):
        data = GetData(self.p1, period=self.period, interval=self.interval).get_stock_history
        # calculate Conversion Line (Tenkan)
        # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2
        nine_period_high = data['High'].rolling(window=9).max()
        nine_period_low = data['Low'].rolling(window=9).min()
        data['tenkan_sen'] = (nine_period_high + nine_period_low) / 2

        # Kijun-sen (Base Line): (26-period high + 26-period low)/2
        twtysix_period_high = data['High'].rolling(window=26).max()
        twtysix_period_low = data['Low'].rolling(window=26).min()
        data['kijun_sen'] = (twtysix_period_high + twtysix_period_low) / 2

        # Chikou-span (Trend strength indicator): Close shifted 26 days behind
        data['chickou_span'] = data['Close'].shift(-26)

        # Senkou-span-a (Resistance line): (conversion line + base line) /2 -- shifted 26 days ahead
        data['senkou_span_a'] = ((data['tenkan_sen'] + data['kijun_sen']) / 2).shift(26)

        # Senkou-span-b (Support line): (52-period high + 52-period low) /2 -- shifted 26 days ahead
        ftytwo_period_high = data['High'].rolling(window=52).max()
        ftytwo_period_low = data['Low'].rolling(window=52).min()
        data['senkou_span_b'] = ((ftytwo_period_high + ftytwo_period_low) / 2).shift(26)

        # Calculate the RSI
        delta = data['Close'].diff()
        up = delta.clip(lower=0)
        down = -1*delta.clip(upper=0)
        ema_up = up.ewm(com=13, adjust=False).mean()
        ema_down = down.ewm(com=13, adjust=False).mean()
        data['rs'] = ema_up/ema_down

        return data


class ViewData(Analysis):
    def __init_(self, symbol):
        self.symbol = symbol
        super().__init__(self.symbol)

    def compare_with_index(self):
        # TODO: plot a comparison with the S&P500 or NASDAQ

        return

    def plot_ichimoku(self):
        # TODO: add RSI oscillator to volume
        # Get data from Analysis class
        data = super().ichimoku()
        # Setup plot based on nightclouds MPL style with no grid
        s = mpf.make_mpf_style(base_mpf_style='nightclouds', gridstyle='')
        setup = dict(type='candle', style=s, volume=True, figscale=2, scale_width_adjustment=dict(candle=1.5),
                     fill_between=dict(y1=data['senkou_span_a'].values, y2=data['senkou_span_b'].values, alpha=0.25),
                     tight_layout=False)
        # Create Ichimoku lines to add to the plot
        ap0 = [mpf.make_addplot(data['tenkan_sen'], color='g', width=0.8, alpha=0.75),
               mpf.make_addplot(data['kijun_sen'], color='r', width=0.8, alpha=0.75),
               mpf.make_addplot(data['chickou_span'], color='pink', linestyle='dotted', width=0.4),
               mpf.make_addplot(data['senkou_span_a'], color='y', width=0.5, alpha=0.5),
               mpf.make_addplot(data['senkou_span_b'], color='purple', width=0.5, alpha=0.5)]
        ap1 = mpf.make_addplot(data['rs'], panel=1)
        # Plot data and add lines
        mpf.plot(data, **setup, addplot=[ap0,ap1], title=f'\n {symbol.upper()}, {datetime.now().strftime("%m/%d/%Y")}')


if __name__ == "__main__":
    symbol = input("Please input symbol: ")
    period = input("6mo/1mo: ")
    interval = input("1d/15m: ")
    ViewData(symbol=symbol, period=period, interval=interval).plot_ichimoku()
