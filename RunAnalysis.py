import yfinance as yf
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplfinance as mpf
import os
import io
from PIL import Image
import pickle
from datetime import datetime
from DataScrape import GetData


class Analysis:

    def __init__(self, symbol, days=25, period="1mo", interval="15m", symbol2=None, save=None):
        self.p1 = symbol
        self.p2 = symbol2
        self.days = days
        self.period = period
        self.interval = interval
        self.save = save
        self.path = "\PycharmProjects\Options\output"
        self.stocklist = []
        # define series for Ichimoku
        self.tenkan = {}
        self.kijun = {}
        self.chikou = {}
        self.senkou_a = {}
        self.senkou_b = {}

    def ichimoku(self):
        # TODO: need to re-write the calculations for the lines into DataFrames so I can use the shift() fn to plot

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
        rs = ema_up/ema_down
        data['rsi'] = 100-(100/(1+rs))
        data['rsi_high'] = 70
        data['rsi_low'] = 30

        return data


class ViewData(Analysis):
    def __init_(self, save=False):
        self.save = save
        super().__init__(self.symbol)

    def get_file_list(self):
        # TODO: sort by the newest file
        file_list = []
        for i in os.listdir(path=os.environ["USERPROFILE"]+self.path):
            if i[:len(symbol)] == symbol.upper():
                file_list.append(i)

        return file_list

    def load_chart(self, file):
        img = pickle.load(open(os.environ["USERPROFILE"]+self.path+f'\{file}', "rb"))

        return Image.open(img).show()

    def compare_with_index(self):
        # TODO: plot a comparison with the S&P500 or NASDAQ
        return

    def plot_ichimoku(self):
        # TODO: add RSI oscillator to volume
        # Get data from Analysis class
        data = super().ichimoku()
        # Set variable to store image in bytes
        buf300dpi = io.BytesIO()
        # Setup plot based on nightclouds MPL style with no grid
        s = mpf.make_mpf_style(base_mpf_style='nightclouds', gridstyle='')
        setup = dict(type='candle', style=s, volume=True, figscale=2,
                     scale_width_adjustment=dict(candle=1.5, volume=1.5),
                     fill_between=dict(y1=data['senkou_span_a'].values, y2=data['senkou_span_b'].values, alpha=0.25),
                     tight_layout=False)
        # Create Ichimoku lines to add to the plot
        ap0 = [mpf.make_addplot(data['tenkan_sen'], color='lime', width=0.9, alpha=0.75),
               mpf.make_addplot(data['kijun_sen'], color='r', width=0.8, alpha=0.75),
               mpf.make_addplot(data['chickou_span'], color='pink', linestyle='dotted', width=0.4),
               mpf.make_addplot(data['senkou_span_a'], color='y', width=0.5, alpha=0.5),
               mpf.make_addplot(data['senkou_span_b'], color='purple', width=0.5, alpha=0.5),
               mpf.make_addplot(data['rsi'], color='white', panel=1),
               mpf.make_addplot(data['rsi_high'], color='pink', alpha=0.5, panel=1),
               mpf.make_addplot(data['rsi_low'], color='pink', alpha=0.5, panel=1)]
        # Save the file if true, if false plot
        if self.save:
            mpf.plot(data,
                     **setup,
                     savefig=dict(fname=buf300dpi,
                                  dpi=300,
                                  pad_inches=0.25),
                     addplot=ap0,
                     title=f'\n {symbol.upper()}, {datetime.now().strftime("%m/%d/%Y")}')
        else:
            mpf.plot(data, **setup, addplot=ap0, title=f'\n {symbol.upper()}, {datetime.now().strftime("%m/%d/%Y")}')

        return buf300dpi


if __name__ == "__main__":
    symbol = input("Please input symbol: ")
    period = input("6mo/1mo/5d/1d: ")
    interval = input("1d/15m/5m/1m: ")
    view = ViewData(symbol=symbol, period=period, interval=interval, save=True)
    image = view.plot_ichimoku()
    to_view = input("View file? (yes/hist/no): ")
    if to_view.lower() == "yes":
        Image.open(image).show()
    elif to_view.lower() == "hist":
        try:
            view.load_chart(view.get_file_list()[0])
        except ValueError:
            print("No charts saved")
    else:
        filename = f'\PycharmProjects\Options\output\{symbol.upper()}-{datetime.now().strftime("%m-%d-%Y")}.p'
        pickle.dump(image, open(os.environ["USERPROFILE"]+f'{filename}', "wb"))


"""
To check existing charts:
1) get the list of files saved for the symbol --> file_list = view.get_file_list()
2) view the list of files to select the correct date --> file_list
3) set file == file_list[INDEX OF CORRECT DATE]
4) load the chart --> view.load_chart(file)

"""
