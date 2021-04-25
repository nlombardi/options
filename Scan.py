import Ichimoku
from DataScrape import GetData
from multiprocessing.dummy import Pool as ThreadPool
import itertools
from pick import pick
# for saving files
import os
import pickle
import pandas as pd
from datetime import datetime
# for testing
import time

class Alert(Ichimoku.Analysis):
    def __main__(self, period: str = False, interval: str = False):
        super().__init__(self.symbol)
        self.period = period if period else super().__init__(self.period)
        self.interval = interval if interval else super().__init__(self.interval)

    def check_conversion(self, data):
        if data['tenkan_sen'][-1] > data['kijun_sen'][-1] \
                and data['tenkan_sen'][-2] <= data['kijun_sen'][-2]:
            return "up"
        elif data['tenkan_sen'][-1] < data['kijun_sen'][-1] \
                and data['tenkan_sen'][-2] >= data['kijun_sen'][-2]:
            return "down"
        else:
            return False

    def check_cloud(self, data):
        if data['Close'][-1] > max(data['senkou_span_a'][-1], data['senkou_span_b'][-1]):
            return "up"
        elif data['Close'][-1] < min(data['senkou_span_a'][-1], data['senkou_span_b'][-1]):
            return "down"
        else:
            return False

    def check_rsi(self, data):
        # looks for RSI that matches a trending market for pairing with Ichimoku trends
        last_entry = round(data['rsi'][-1], 0)
        second_last_entry = round(data['rsi'][-2], 0)
        increasing = last_entry > second_last_entry
        decreasing = last_entry < second_last_entry
        four_period = round(data['rsi'][-4:], 0)
        four_period_avg = round(four_period.mean(), 0)
        # check if the rsi is trending up/down or hit support/resistance and bounced/fell (4 --> 1hr on 15min interval)
        if last_entry > four_period_avg and increasing \
                or last_entry > 40 and (x < 40 for x in four_period) and increasing:
            return "up"
        elif last_entry > four_period_avg and decreasing \
                or last_entry < 60 and (x > 60 for x in four_period) and decreasing:
            return "down"

    def check_volume(self, data):
        # TODO: subtract first period date and last period date to get difference
        # Checks if the volume on the stock is greater than 400,000/day
        if interval == "15m":
            t = 26
        elif interval == "1h":
            t = 7
        else:
            t = 26
        t22 = t*22
        last_day_vol = data[-t:].Volume.sum() # one day for 15min interval
        month_avg = round(data[-t22:].Volume.sum()/22, 0)
        if 400000 < month_avg < last_day_vol:
            return True
        else:
            return False

    def find_entry(self):
        data = super().ichimoku(period=self.period, interval=self.interval)
        if data.empty:
            pass
        else:
            if self.check_conversion(data) == "up" \
                    and self.check_cloud(data) == "up"\
                    and self.check_rsi(data) == "up"\
                    and self.check_volume(data):
                print("Conversion up and price above cloud!")
                print(f"Symbol: {self.symbol}, Period: {self.period}, Interval: {self.interval}")
                up = {'Symbol': self.symbol, 'Period': self.period, 'Interval': self.interval, 'Buy/Sell': "BUY"}
                return up
            elif self.check_conversion(data) == "down" \
                    and self.check_cloud(data) == "down" \
                    and self.check_rsi(data) == "down"\
                    and self.check_volume(data):
                print("Conversion down and price below cloud!")
                print(f"Symbol: {self.symbol}, Period: {self.period}, Interval: {self.interval}")
                down = {'Symbol': self.symbol, 'Period': self.period, 'Interval': self.interval, 'Buy/Sell': "SELL"}
                return down


def scan_list(symbol, period=None, interval=None):
    return Alert(symbol=symbol, period=period, interval=interval).find_entry()


if __name__ == "__main__":
    period, index1 = pick(['6mo', '1mo', '5d', '1d'], 'Select a time period: ')
    interval, index2 = pick(['1d', '15m', '5m', '1m'], 'Select an interval: ')
    source, index3 = pick(['Nasdaq', 'S&P500'], 'Select the stock list source: ')
    entry = {'Symbol': [], 'Period': [], 'Interval': [], 'Buy/Sell': []}
    stock_list = GetData(source=str(source)).get_stock_list()
    print("Starting to scan for entry points!")
    # Pool requests to get data in parallel (much faster)
    tp = ThreadPool(50)
    entry_list = tp.starmap(scan_list, zip(stock_list, itertools.repeat(period), itertools.repeat(interval)))
    tp.close()
    tp.join()
    for i in entry_list:
        if i:
            entry["Symbol"].append(i["Symbol"])
            entry["Period"].append(i["Period"])
            entry["Interval"].append(i["Interval"])
            entry["Buy/Sell"].append(i["Buy/Sell"])
    # Save results
    with open(os.environ['USERPROFILE'] +
              "\\PycharmProjects\\Options\\output\\EntryList_" + source + "_"
              + datetime.now().strftime("%m-%d-%Y") + ".p", "wb") as f:
        pickle.dump(entry, f)
    f.close()
    # convert to dataframe and save as csv
    df = pd.DataFrame.from_dict(entry)
    df.to_csv(os.environ['USERPROFILE'] +
              "\\PycharmProjects\\Options\\output\\EntryList_" + source + "_"
              + datetime.now().strftime("%m-%d-%Y") + ".csv")

