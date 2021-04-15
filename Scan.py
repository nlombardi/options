import Ichimoku
from DataScrape import GetData
import pickle
import os
import pandas as pd
from datetime import datetime

stock_list = GetData().get_stock_list()


class Alert(Ichimoku.Analysis):
    def __main__(self):
        super().__init__(self.symbol)

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

    def find_entry(self):
        # TODO: need to add a dictionary to append to when one of the requirements is met
        data = super().ichimoku()
        entry_list = {'Symbol': str, 'Period': int, 'Interval': int, 'Buy/Sell': str}
        if data.empty:
            pass
        else:
            if self.check_conversion(data) == "up" and self.check_cloud(data) == "up":
                print("Conversion up and price above cloud!")
                print(f"Symbol: {self.symbol}, Period: {self.period}, Interval: {self.interval}")
                entry_list = {'Symbol': self.symbol, 'Period': self.period,
                              'Interval': self.interval, 'Buy/Sell': "BUY"}
                return entry_list
            elif self.check_conversion(data) == "down" and self.check_cloud(data) == "down":
                print("Conversion down and price below cloud!")
                print(f"Symbol: {self.symbol}, Period: {self.period}, Interval: {self.interval}")
                entry_list = {'Symbol': self.symbol, 'Period': self.period,
                              'Interval': self.interval, 'Buy/Sell': "SELL"}
                return entry_list


if __name__ == "__main__":
    entry_list = []
    for i in stock_list:
        entry_list.append(Alert(symbol=i).find_entry())
    # pickle results
    with open(os.environ['USERPROFILE'] +
              "\\PycharmProjects\\Options\\output\\EntryList_"+datetime.now().strftime("%m/%d/%Y")+".p", "wb") as f:
        pickle.dumps(entry_list, f)
    f.close()
    # convert to dataframe and save as csv
    df = pd.DataFrame.from_dict(dict(entry_list))
    df.to_csv(os.environ['USERPROFILE'] +
              "\\PycharmProjects\\Options\\output\\EntryList_"+datetime.now().strftime("%m/%d/%Y")+".csv")