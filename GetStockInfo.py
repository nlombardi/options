import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time


class LookupCompany:

    def __init__(self, defaultAPI: {"yahoo", "finnhub", "bloomberg"}, symbol):
        self.defaultAPI = defaultAPI
        self.symbol = symbol
        self.date = datetime.today()

    def getDetail(self, symbol=""):
        if self.defaultAPI == "yahoo":
            url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/get-detail"
            headers = {
                'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
                'x-rapidapi-key': "a859ce6386msh8123849ccfaddb3p1b6464jsnfa3a574694ed"
            }
            querystring = {"region": "US", "lang": "en", "symbol": self.symbol}
        elif self.defaultAPI == "finnhub":
            url = "https://finnhub-realtime-stock-price.p.rapidapi.com/stock/price-target"
            headers = {
                'x-rapidapi-host': "finnhub-realtime-stock-price.p.rapidapi.com",
                'x-rapidapi-key': "a859ce6386msh8123849ccfaddb3p1b6464jsnfa3a574694ed"
            }
            querystring = {"symbol": self.symbol}
        elif self.defaultAPI == "bloomberg":
            url = "https://bloomberg-market-and-financial-news.p.rapidapi.com/market/get-full"
            headers = {
                'x-rapidapi-host': "bloomberg-market-and-financial-news.p.rapidapi.com",
                'x-rapidapi-key': "a859ce6386msh8123849ccfaddb3p1b6464jsnfa3a574694ed"
            }
            querystring = {"id": self.symbol}
        else:
            url = "https://bloomberg-market-and-financial-news.p.rapidapi.com/market/get-chart"
            headers = {
                'x-rapidapi-host': "bloomberg-market-and-financial-news.p.rapidapi.com",
                'x-rapidapi-key': "a859ce6386msh8123849ccfaddb3p1b6464jsnfa3a574694ed"
            }
            querystring = {"interval": "m3", "id": self.symbol}

        response = requests.request("GET", url, headers=headers, params=querystring)
        response.status_code
        response.raise_for_status()

        return response.json()
        print(response.text)

    def getHistory(self, symbol=""):
        url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/get-detail"
        date = datetime.today()
        three_month_lag = date - timedelta(days=date.day)
        d1 = time.time()
        d2 = d1 - (2629743 * 3)  # takes Epoch time and subtracts 3 months in seconds (1 month = 2629743 seconds)

        query = {"frequency": "1d", "filter": "history", "period1": d2,  # Gets prices last 57 days
                     "period2": d1, "symbol": self.symbol}

        headers = {
            'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
            'x-rapidapi-key': "a859ce6386msh8123849ccfaddb3p1b6464jsnfa3a574694ed"
        }

        response = requests.request("GET", url, headers=headers, params=query)

        return response.json()
        print(response.text)



LookupCompany = LookupCompany(defaultAPI="yahoo", symbol="TSLA")
data = LookupCompany.getDetail()
df = pd.DataFrame.from_dict(data)
df.to_csv(f"C:/Users/../{LookupCompany.symbol}.csv")
