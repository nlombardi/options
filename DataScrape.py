import yfinance as yf
import requests
import pandas as pd
import io
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os


class GetData:

    def __init__(self, symbol=None, raw=None, save=None, period="1mo", interval="15m", source="Nasdaq"):
        if source is None:
            source = {"Nasdaq", "S&P500"}
        self.url = f"https://quotes.freerealtime.com/quotes/symbol/Quote?symbol={symbol}"
        self.symbol = symbol
        self.symbols = []
        self.data = []
        self.content = None
        self.raw = raw
        self._tikr_data = None
        self._tikr_hist = None
        self._quote = None
        self._path = "/PycharmProjects/Options/data/"
        self.save = save
        self.period = period
        self.interval = interval
        self.source = source

        # Webdriver options
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-setuid-sandbox")

    def open_driver(self):
        driver = webdriver.Chrome(executable_path=os.environ["USERPROFILE"] + "/PycharmProjects/chromedriver",
                                  options=self.options)
        return driver

    def check_symbol(self):
        if not self.symbol:
            raise ValueError("Symbol not defined")

    def get_stock_list(self):
        """
        Go to Nasdaq stocks page and download the .csv file, replace in directory
        """
        for tries in range(5):
            try:
                if self.source == "Nasdaq":
                    r = requests.get("https://pkgstore.datahub.io/core/nasdaq-listings/nasdaq-listed_csv/data/"
                                     "7665719fb51081ba0bd834fde71ce822/nasdaq-listed_csv.csv")
                elif self.source == "S&P500":
                    r = requests.get("https://datahub.io/core/s-and-p-500-companies-financials/r/constituents"
                                     "-financials.csv")
                else:
                    raise ValueError("Stock list source not defined (Nasdaq or S&P500)")
                if r.status_code != 200:
                    raise ValueError("Invalid response from webserver")
                # Scrape results
                self.symbols = pd.read_csv(io.StringIO(r.content.decode("utf-8")))
                print("Success")
                break
            except Exception as e:
                print(f"Request failed, Exception: {e}")
        return self.symbols["Symbol"].tolist()

    def geturl(self):
        self.check_symbol()
        # accesses freerealtime quotes and returns the raw data as well as the quote
        driver = self.open_driver()
        driver.get(self.url)
        timeout = 2
        try:
            WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME,
                                                                                   "content")))
            if self.raw is True:
                self.raw = driver.page_source
            self._quote = driver.find_element_by_class_name("qmod-last").text
            driver.close()
        except TimeoutException:
            driver.quit()
            print("Timed out..")

    def get_real_time(self):
        # Takes symbol and index input and looks up the real time trading and posts them
        self.geturl()
        return print(self._quote)

    def get_stock_data(self):
        self.check_symbol()
        # Takes a symbol and grabs more detailed Ticker data
        self._tikr_data = yf.Ticker(f"{self.symbol}")
        return self._tikr_data

    def get_stock_history(self):
        self.get_stock_data()
        try:
            self._tikr_hist = self._tikr_data.history(period=self.period, interval=self.interval)
            if self.save is True:
                self._tikr_hist.to_csv(os.environ["USERPROFILE"] + self._path + f"{self.symbol}.csv")
        except Exception:
            self._tikr_hist = pd.DataFrame()
        finally:
            return self._tikr_hist
