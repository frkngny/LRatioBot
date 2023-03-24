from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
from Utilities import COLUMNS


# We use selenium to get price and l-ratio from coinglass
class SScraper:
    def __init__(self):

        # page to get l-ratio
        self.l_ratio_driver = webdriver.Chrome(r'C://chromedriver//chromedriver.exe')
        self.l_ratio_driver.get("https://www.coinglass.com/en/LongShortRatio")
        # when you inspect the html codes of the page >
        self.ls_rate_class = "bybt-ls-rate"  # this is the class of the html tag which keeps related information
        self.LSRatioMap = {"Overall": 0, "Binance": 1, "OKX": 2}  # tag indexes
        self.LSPositionMap = {"Long": 0, "Short": 1}  # position indexes

        # page to get price
        self.price_driver = webdriver.Chrome(r'C://chromedriver//chromedriver.exe')
        self.price_driver.get("https://www.coinglass.com")
        self.PriceMap = {"Binance": 16}  # index of the tag in html
        self.price_class = "ant-table-cell"  # class of the html tag which keeps related info

        self.symbol = "BTC"

        self.csv_file = None

        self.data = dict()

    def store_data(self, csv_file: str):
        self.csv_file = csv_file
        nowtime = int(time.time() * 1000)

        # get the div where ls rate information lays
        ls_rates = self.l_ratio_driver.find_elements(By.CLASS_NAME, self.ls_rate_class)[self.LSRatioMap["Binance"]]
        l_rate_div = ls_rates.find_elements(By.TAG_NAME, "div")[self.LSPositionMap["Long"]]  # get l ratio tag
        l_ratio = float(l_rate_div.text.replace('%', '')) / 100

        # same for price
        prices = self.price_driver.find_elements(By.CLASS_NAME, self.price_class)[self.PriceMap["Binance"]]
        price = prices.find_elements(By.TAG_NAME, "div")[0]
        price = float(price.text.replace('$', ''))

        # create dataframe
        self.data[COLUMNS.TIME] = nowtime
        self.data[COLUMNS.SYMBOL] = self.symbol
        self.data[COLUMNS.LRATIO] = l_ratio
        self.data[COLUMNS.PRICE] = price

        # write into csv
        df1 = pd.read_csv(self.csv_file)
        df2 = pd.DataFrame()
        for k in df1.keys():
            try:
                df2[k] = [self.data[k]]
            except:
                df2[k] = ""
        try:
            t1 = df1[COLUMNS.TIME].values[-1]
            t2 = df2[COLUMNS.TIME].values[-1]
            df2[COLUMNS.TIME_DIFF] = [int(t2 - t1)]
        except:
            pass

        df2.to_csv(self.csv_file, mode='a', index=False, header=False)

    def end_session(self):
        """
        this function ends the session of the object
        """
        self.price_driver.close()
        self.l_ratio_driver.close()
    
    def refresh_session(self):
        """
        this function refreshes the page in case any error
        """
        self.l_ratio_driver.refresh()
        self.price_driver.refresh()
