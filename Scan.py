import Ichimoku
from DataScrape import GetData
import os
import concurrent.futures
import pickle
from pick import pick
import pandas as pd
from datetime import datetime


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
        last_entry = round(data['rsi'][-1], 0)
        second_last_entry = round(data['rsi'][-2], 0)
        increasing = last_entry > second_last_entry
        decreasing = last_entry < second_last_entry
        four_period = round(data['rsi'][-4:], 0)
        four_period_avg = round(four_period.mean(), 0)
        # check if the rsi is trending up/down or hit support/resistance and bounced/fell (4 --> 1hr on 15min interval)
        if last_entry > four_period_avg and increasing \
                or (x < 30 for x in four_period) and increasing:
            return "up"
        elif last_entry > four_period_avg and decreasing \
                or (x > 70 for x in four_period) and decreasing:
            return "down"

    def check_volume(self, data):
        # Checks if the volume on the stock is greater than the average volume and over a certain threshold (ie, 50,000)
        pass

    def find_entry(self):
        # TODO: add a volume check to make sure the volume is increasing on the stock
        data = super().ichimoku(period=self.period, interval=self.interval)
        if data.empty:
            pass
        else:
            if self.check_conversion(data) == "up" \
                    and self.check_cloud(data) == "up"\
                    and self.check_rsi(data) == "up":
                print("Conversion up and price above cloud!")
                print(f"Symbol: {self.symbol}, Period: {self.period}, Interval: {self.interval}")
                up = {'Symbol': self.symbol, 'Period': self.period, 'Interval': self.interval, 'Buy/Sell': "BUY"}
                return up
            elif self.check_conversion(data) == "down" \
                    and self.check_cloud(data) == "down" \
                    and self.check_rsi(data) == "down":
                print("Conversion down and price below cloud!")
                print(f"Symbol: {self.symbol}, Period: {self.period}, Interval: {self.interval}")
                down = {'Symbol': self.symbol, 'Period': self.period, 'Interval': self.interval, 'Buy/Sell': "SELL"}
                return down

#
# def scan_list(symbol, period=None, interval=None):
#     entry = Alert(symbol=symbol, period=period, interval=interval).find_entry()
#     if entry:
#         return entry
#     else:
#         pass


if __name__ == "__main__":
    period, index1 = pick(['6mo', '1mo', '5d', '1d'], 'Select a time period: ')
    interval, index2 = pick(['1d', '15m', '5m', '1m'], 'Select an interval: ')
    source, index3 = pick(['Nasdaq', 'S&P500'], 'Select the stock list source: ')
    entry_list = []
    stock_list = GetData(source=str(source)).get_stock_list()
    print("Starting to scan for entry points!")
    for i in stock_list:
        entry_list.append(Alert(symbol=i, period=period, interval=interval).find_entry())
    # pickle results
    with open(os.environ['USERPROFILE'] +
              "\\PycharmProjects\\Options\\output\\EntryList_" + source + "_"
              + datetime.now().strftime("%m-%d-%Y") + ".p", "wb") as f:
        pickle.dump(entry_list, f)
    f.close()
    # convert to dataframe and save as csv
    df = pd.DataFrame.from_dict(entry_list)
    df.to_csv(os.environ['USERPROFILE'] +
              "\\PycharmProjects\\Options\\output\\EntryList_" + source + "_"
              + datetime.now().strftime("%m-%d-%Y") + ".csv")

    # # MULTIPROCESSING
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     entry_list = executor.map(scan_list, stock_list)