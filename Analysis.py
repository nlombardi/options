import yfinance as yf
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplfinance as mpf
import matplotlib.dates as dates
import os
from statistics import mean
import datetime
from DataScrape import GetData


class Analysis:

    def __init__(self, symbol, days=25, period="3mo", interval="1d", symbol2=None, save=None):
        self.p1 = symbol
        self.p2 = symbol2
        self.days = days
        self.period = period
        self.interval = interval
        self.save = save
        self.path = "/PycharmProjects/Options/output/"
        self.stocklist = []
        # define series for Ichimoku
        self.tenkan = []
        self.kijun = []
        self.chikou = []
        self.senkou_a = []
        self.senkou_b = []


    def plotData(self):
        # pull multiple symbols and plot against
        fig, ax = plt.subplots()
        ax.grid()
        # if only one symbol
        if not self.p2:
            data = yf.download(f"{self.p1}")
            p1 = ax.plot(data.tail(self.days).index,
                         data["Close"].tail(self.days),
                         color="red", marker="o",
                         label=self.p1)
            ax.set_xlabel("Date", fontsize=12)
            ax.set_xticklabels(ax.get_xticks(), rotation=90, fontsize=8)
            ax.set_ylabel("Close Price", fontsize=12)
            if self.save is True:
                fig.savefig(
                    executable_path=os.environ["USERPROFILE"] + self.path + f"{self.p1}_last{self.days}days.jpg",
                    format="jpeg",
                    bbox_inches="tight",
                    dpi=300)
        elif self.p2:
            data = yf.download(f"{self.p1} {self.p2}")
            ax.set_xlabel("Date", fontsize=12)
            ax.set_xticklabels(ax.get_xticks(), rotation=90, fontsize=8)
            ax.set_ylabel("Close Price", fontsize=12)
            # First Line
            p1 = ax.plot(data.tail(self.days).index,
                         data["Close"].tail(self.days),
                         color="red", marker="o",
                         label=self.p1)
            # Second Line
            ax2 = ax.twinx()
            p2 = ax2.plot(data.tail(10).index,
                          data["Close"][self.p2].tail(10),
                          color="green", marker="o",
                          label=self.p2)
            # format graph
            lns = p1 + p2
            labs = [l.get_label() for l in lns]
            ax.legend(lns, labs, loc=0)
            if self.save is True:
                fig.savefig(
                    executable_path=os.environ[
                                        "USERPROFILE"] + self.path + f"{self.p1}_{self.p2}_last{self.days}days.jpg",
                    format="jpeg", dpi=300, bbox_inches="tight")
        # show / save graph
        plt.show()

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

    def Ichimoku(self):
        # TODO: plot Ichimoku
        data = GetData(self.p1, period=self.period, interval=self.interval).get_stock_history
        # calculate Conversion Line (Tenkan)
        for i in range(len(data)-8):
            highest_high_9ma = round(data["High"].iloc[:i+9].max(), 4)
            lowest_low_9ma = round(data["Low"].iloc[:i+9].min(), 4)
            self.tenkan.append({"Date": data.iloc[i+8].name.date(), "Avg": mean([highest_high_9ma, lowest_low_9ma])})
        """
        calculate Base Line (Kijun), Trend Strength (Chikou, 26 day price lag), 
        Resistance (Senkou_a), Support (Senkou_b) --> 26 days forward calculated from Kijun Line
        """
        for i in range(len(data)-25):
            highest_high_26ma = round(data["High"].iloc[:i+26].max(),4)
            lowest_low_26ma = round(data["Low"].iloc[:i+26].min(), 4)
            if i+52 < len(data):
                highest_high_52ma = round(data["High"].iloc[:i+52].max(),4)
                lowest_low_52ma = round(data["Low"].iloc[:i+52].min(), 4)
            elif i+52 > len(data):
                highest_high_52ma = round(data["High"].iloc[i:len(data)].max(),4)
                lowest_low_52ma = round(data["Low"].iloc[i:len(data)].min(), 4)
            self.kijun.append({"Date": data.iloc[i+25].name.date(), "Avg": mean([highest_high_26ma, lowest_low_26ma])})
            self.chikou.append({"Date": data.iloc[i].name.date(), "Price": data["Close"].iloc[i+25]})
            self.senkou_a.append({"Date": data.iloc[51].name.date() + datetime.timedelta(days=i),
                                  "Avg": mean([self.tenkan[i+17]['Avg'], self.kijun[i]['Avg']])})
            self.senkou_b.append({"Date": data.iloc[51].name.date() + datetime.timedelta(days=i),
                                  "Avg": mean([highest_high_52ma, lowest_low_52ma])})
