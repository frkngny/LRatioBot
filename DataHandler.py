from coinglassApi import CoinGlassAPI
from Utilities import load_io_params
from _selenium import SScraper


# Handle the object you want to get data from Coinglass or Selenium
# for coinglass, use collect_data_and_store function
class DataHandler:
    def __init__(self, method: str):
        if method.lower() == "coinglass":
            self.io_params = load_io_params()
            self.disabled = [""]  # list to disable to get data for (e.g. "open_interest")

            self.cgApi = CoinGlassAPI(self.io_params, self.disabled, "input_csv")
        elif method.lower() == "selenium":
            self.slnm = SScraper()

    def collect_data_and_store(self):
        self.cgApi.common_market()  # collect from api and write into db

    def scrape_data_and_store(self, input_csv):
        self.slnm.store_data(input_csv)

    def refresh_selenium(self):
        self.slnm.refresh_session()

    def close_selenium(self):
        self.slnm.end_session()